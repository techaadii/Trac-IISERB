"""
HMM Routes
==========
GET  /api/hmm/matrix           — full transition probability matrix
GET  /api/hmm/ranked/{cam}     — next cameras ranked by probability
POST /api/hmm/feedback         — human confirms/denies a transition
GET  /api/hmm/log              — recent feedback log
"""

import logging

from fastapi import APIRouter, HTTPException

from backend.app.core.hmm_engine import (
    get_feedback_log,
    get_transition_matrix,
    ranked_cameras,
    record_transition,
    transition_probs,
)
from backend.app.schemas.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    TransitionMatrixResponse,
    TransitionProbResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/matrix", response_model=TransitionMatrixResponse,
            summary="Full transition probability matrix")
async def get_matrix():
    """
    Returns P(from → to) for every camera pair.
    On cold start all reachable neighbours have equal probability.
    Probabilities improve as humans submit feedback.
    """
    return TransitionMatrixResponse(matrix=get_transition_matrix())


@router.get("/ranked/{camera_id}", response_model=TransitionProbResponse,
            summary="Next cameras ranked by transition probability")
async def get_ranked(camera_id: str):
    """
    Given a camera, returns its neighbours sorted by how likely
    a vehicle is to move there next, based on learned counts.
    """
    from backend.app.core.camera_network import CAMERAS
    if camera_id not in CAMERAS:
        raise HTTPException(404, f"Camera '{camera_id}' not found.")

    probs = transition_probs(camera_id)
    return TransitionProbResponse(
        from_cam      = camera_id,
        probabilities = probs,
    )


@router.post("/feedback", response_model=FeedbackResponse,
             summary="Submit human feedback to improve HMM")
async def submit_feedback(request: FeedbackRequest):
    """
    Called when an operator confirms or denies that a vehicle
    moved from one camera to another.

    confirmed=True  → increments transition count, sharpens future predictions
    confirmed=False → logged for audit, does not affect probabilities
    """
    from backend.app.core.camera_network import CAMERAS

    if request.from_cam not in CAMERAS:
        raise HTTPException(404, f"Camera '{request.from_cam}' not found.")
    if request.to_cam not in CAMERAS:
        raise HTTPException(404, f"Camera '{request.to_cam}' not found.")

    record_transition(
        from_cam  = request.from_cam,
        to_cam    = request.to_cam,
        confirmed = request.confirmed,
    )

    new_probs = transition_probs(request.from_cam)

    return FeedbackResponse(
        success   = True,
        from_cam  = request.from_cam,
        to_cam    = request.to_cam,
        confirmed = request.confirmed,
        new_probs = new_probs,
    )


@router.get("/log", summary="Recent human feedback events")
async def get_log(limit: int = 100):
    """Returns the last N feedback events for audit purposes."""
    return {"log": get_feedback_log(limit=limit)}