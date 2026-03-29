"""
HMM Engine
==========
Maintains transition counts in SQLite and exposes:
  - record_transition(from_cam, to_cam)  : called when human confirms a sighting
  - transition_probs(from_cam)           : probability dict for next camera
  - ranked_cameras(from_cam)             : neighbours sorted by probability
  - viterbi(observations)                : most likely path given similarity scores

Cold start:
  - Zero counts → all neighbours get equal probability 1/N (uniform prior)
  - Laplace smoothing (alpha=1) ensures no transition is ever zero probability
  - As humans confirm sightings, counts grow and probabilities sharpen
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from backend.app.core.camera_network import ADJACENCY, CAMERAS, ROOT_CAMERA

logger = logging.getLogger(__name__)

DB_PATH = Path("backend/data/hmm.db")
ALPHA   = 1.0   # Laplace smoothing — keeps unseen transitions non-zero


def init_db():
    """Create SQLite tables if they don't exist. Safe to call multiple times."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transition_counts (
                from_cam  TEXT NOT NULL,
                to_cam    TEXT NOT NULL,
                count     INTEGER DEFAULT 0,
                PRIMARY KEY (from_cam, to_cam)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                from_cam   TEXT NOT NULL,
                to_cam     TEXT NOT NULL,
                confirmed  INTEGER NOT NULL,  -- 1=hit, 0=miss
                timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("HMM database ready at %s", DB_PATH)


# ── Transition counts ─────────────────────────────────────────────────────────

def record_transition(from_cam: str, to_cam: str, confirmed: bool = True):
    """
    Called when a human confirms or denies a vehicle sighting.
    confirmed=True  → vehicle moved from from_cam to to_cam (increment count)
    confirmed=False → logged for audit but count not incremented
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Log every feedback event
        conn.execute(
            "INSERT INTO feedback_log (from_cam, to_cam, confirmed) VALUES (?,?,?)",
            (from_cam, to_cam, 1 if confirmed else 0)
        )
        if confirmed:
            # Upsert — increment if exists, insert if not
            conn.execute("""
                INSERT INTO transition_counts (from_cam, to_cam, count)
                VALUES (?, ?, 1)
                ON CONFLICT(from_cam, to_cam)
                DO UPDATE SET count = count + 1
            """, (from_cam, to_cam))
        conn.commit()


def get_counts(from_cam: str) -> Dict[str, int]:
    """Return raw transition counts from from_cam to each neighbour."""
    neighbours = list(ADJACENCY.get(from_cam, set()))
    if not neighbours:
        return {}

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT to_cam, count FROM transition_counts WHERE from_cam = ?",
            (from_cam,)
        ).fetchall()

    count_map = {row[0]: row[1] for row in rows}
    # Fill zeros for neighbours with no observations yet
    return {nb: count_map.get(nb, 0) for nb in neighbours}


# ── Probability computation ───────────────────────────────────────────────────

def transition_probs(from_cam: str) -> Dict[str, float]:
    """
    Compute transition probabilities from from_cam to each neighbour.

    Formula (Laplace smoothed):
        P(from → nb) = (count(from→nb) + alpha)
                       ─────────────────────────────────────
                       (sum of all counts from 'from') + alpha * num_neighbours

    Cold start (all counts = 0):
        P(from → nb) = alpha / (alpha * N) = 1/N   ← pure uniform
    """
    counts     = get_counts(from_cam)
    neighbours = list(counts.keys())

    if not neighbours:
        return {}

    n          = len(neighbours)
    total      = sum(counts.values())
    denominator = total + ALPHA * n

    return {
        nb: (counts[nb] + ALPHA) / denominator
        for nb in neighbours
    }


def ranked_cameras(from_cam: str) -> List[Tuple[str, float]]:
    """
    Returns neighbours sorted by transition probability descending.
    [(camera_id, probability), ...]
    On cold start all probabilities are equal — order is alphabetical.
    """
    probs = transition_probs(from_cam)
    return sorted(probs.items(), key=lambda x: x[1], reverse=True)


# ── Viterbi decoder ───────────────────────────────────────────────────────────

def viterbi(
    observations: List[Tuple[str, float]],
    start_cam:    str = ROOT_CAMERA,
) -> List[str]:
    """
    Find the most likely camera path given a sequence of observations.

    observations: list of (camera_id, similarity_score) tuples
                  — one per camera that was actually queried during search
    start_cam:    always ENTRY_CAM

    Returns: list of camera IDs representing the most likely vehicle path

    How it works:
      - Each similarity score is treated as an emission probability
        (higher similarity = more likely the vehicle was at that camera)
      - Transition probabilities come from our learned counts
      - Viterbi finds the path that maximises joint probability
    """
    if not observations:
        return [start_cam]

    camera_ids = [obs[0] for obs in observations]
    scores     = [obs[1] for obs in observations]

    n_steps  = len(camera_ids)
    n_cams   = len(CAMERAS)
    cam_list = list(CAMERAS.keys())
    cam_idx  = {c: i for i, c in enumerate(cam_list)}

    # dp[t][i] = log probability of best path ending at camera i at step t
    NEG_INF = float("-inf")
    dp       = [[NEG_INF] * n_cams for _ in range(n_steps)]
    backptr  = [[-1]      * n_cams for _ in range(n_steps)]

    # ── Initialise at start_cam ───────────────────────────────────────────────
    start_idx        = cam_idx[start_cam]
    dp[0][start_idx] = np.log(max(scores[0], 1e-9))

    # ── Forward pass ──────────────────────────────────────────────────────────
    for t in range(1, n_steps):
        curr_cam  = camera_ids[t]
        emit_prob = max(scores[t], 1e-9)   # emission = similarity score

        for prev_idx, prev_cam in enumerate(cam_list):
            if dp[t-1][prev_idx] == NEG_INF:
                continue

            probs = transition_probs(prev_cam)
            trans = probs.get(curr_cam, ALPHA / (ALPHA * max(len(probs), 1)))

            score = dp[t-1][prev_idx] + np.log(trans) + np.log(emit_prob)

            curr_idx = cam_idx[curr_cam]
            if score > dp[t][curr_idx]:
                dp[t][curr_idx]      = score
                backptr[t][curr_idx] = prev_idx

    # ── Backtrack ─────────────────────────────────────────────────────────────
    # Find best final state
    last_cam_idx = cam_idx[camera_ids[-1]]
    path_indices = [last_cam_idx]

    for t in range(n_steps - 1, 0, -1):
        prev = backptr[t][path_indices[-1]]
        if prev == -1:
            break
        path_indices.append(prev)

    path_indices.reverse()
    return [cam_list[i] for i in path_indices]


# ── Stats helpers ─────────────────────────────────────────────────────────────

def get_transition_matrix() -> Dict[str, Dict[str, float]]:
    """Full probability matrix for all cameras — used by the HMM API endpoint."""
    return {cam_id: transition_probs(cam_id) for cam_id in CAMERAS}


def get_feedback_log(limit: int = 100) -> List[dict]:
    """Recent human feedback events."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """SELECT from_cam, to_cam, confirmed, timestamp
               FROM feedback_log
               ORDER BY id DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [
        {"from_cam": r[0], "to_cam": r[1],
         "confirmed": bool(r[2]), "timestamp": r[3]}
        for r in rows
    ]