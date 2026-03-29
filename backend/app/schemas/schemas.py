"""
schemas.py
==========
Pydantic models for all API request/response shapes.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ── Camera schemas ────────────────────────────────────────────────────────────

class CameraInfo(BaseModel):
    camera_id:    str
    label:        str
    is_root:      bool
    is_terminal:  bool
    neighbours:   List[str]
    image_count:  int = 0
    online:       bool = False
    latency_ms:   Optional[int] = None


class CameraListResponse(BaseModel):
    total:   int
    cameras: List[CameraInfo]


# ── Search schemas ────────────────────────────────────────────────────────────

class SearchResult(BaseModel):
    camera_id:   str
    image_path:  str
    similarity:  float = Field(..., ge=0.0, le=1.0)
    image_url:   Optional[str] = None   # served by FastAPI static files


class CameraSearchResult(BaseModel):
    """Results from searching a single camera."""
    camera_id:    str
    label:        str
    hits:         List[SearchResult]
    best_score:   float = 0.0
    searched:     bool  = True


class SearchSession(BaseModel):
    """
    Full result of one sequential search run.
    Contains per-camera results + the Viterbi-decoded path.
    """
    session_id:       str
    query_type:       str                    # "image" or "text"
    query_text:       Optional[str] = None   # only for text queries
    cameras_queried:  List[CameraSearchResult]
    viterbi_path:     List[str]              # most likely camera sequence
    top_results:      List[SearchResult]     # global top-K across all cameras
    total_images_searched: int = 0


# ── Text search request ───────────────────────────────────────────────────────

class TextSearchRequest(BaseModel):
    query:  str  = Field(..., min_length=3, max_length=500,
                         description="Natural language description e.g. 'red Honda sedan'")
    top_k:  int  = Field(default=10, ge=1, le=50)


# ── HMM schemas ───────────────────────────────────────────────────────────────

class TransitionProbResponse(BaseModel):
    from_cam:      str
    probabilities: Dict[str, float]   # {to_cam: probability}


class TransitionMatrixResponse(BaseModel):
    matrix: Dict[str, Dict[str, float]]   # {from_cam: {to_cam: prob}}


class FeedbackRequest(BaseModel):
    from_cam:   str
    to_cam:     str
    confirmed:  bool = True   # True=vehicle did move this way, False=it didn't


class FeedbackResponse(BaseModel):
    success:    bool
    from_cam:   str
    to_cam:     str
    confirmed:  bool
    new_probs:  Dict[str, float]   # updated probabilities after recording


class FeedbackLogEntry(BaseModel):
    from_cam:   str
    to_cam:     str
    confirmed:  bool
    timestamp:  str


# ── Live stream schemas ───────────────────────────────────────────────────────

class CameraStatus(BaseModel):
    camera_id:    str
    label:        str
    ip:           str
    online:       bool
    last_checked: float        # unix timestamp
    latency_ms:   Optional[int] = None
    snapshot_url: str
    mjpeg_url:    str


class LiveStatusResponse(BaseModel):
    online_count:  int
    offline_count: int
    total:         int
    cameras:       List[CameraStatus]


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:           str
    model_loaded:     bool
    images_cached:    int
    cameras_online:   int
    cameras_total:    int