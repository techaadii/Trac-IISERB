from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Single source of truth for all settings in the backend.
    Ensures that there is no hard coding for the parameters.
    Uses pydantic settings which means:
        - Every setting can be over ridden by a .env file variable without toching the code.
    ATTRIBUTES:  
    1. Details about the model
    2. Details about the data directory
    3. Device related information
    4. Server related issues are there
        
    """

    # Server Details
    host:str="0.0.0.0"
    port:int=8000
    ALLOWED_ORIGINS:list[str]=["https://localhost:3000","https://127.0.0.1:3000"]

    # Model Details
    MODEL_WEIGHTS_PATH:Optional[str]=None
    TOP_K:int=10
    SIMILAIRTY_THRESHOLD:float=0.95

    # Camera Image details
    CAMERA_ROOT:Path=Path("/home/moonlab/Track-IISERB/backend/data/camera")
    IMAGE_EXTENTIONS:list[str]=[".jpg",".png",".jpeg"]
    DATABASE_URL: str = "postgresql+asyncpg://trac_user:trac_password@localhost:5432/trac_db"


    class Config:
        env_file=".env"
        env_file_encoding="utf-8"

settings=Settings()