from pydantic import BaseModel, Field
from typing import Optional
class RouteRequest(BaseModel):
    source: Optional[str] = Field(default="current location", description="Starting point")
    destination: str = Field(..., min_length=2, description="Destination location")
class CommandRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User voice command text")
class SOSRequest(BaseModel):
    user_id: str = Field(..., min_length=2, description="User identifier")
    location: str = Field(..., description="User current location")
    contact: Optional[str] = Field(default="not provided", description="Emergency contact")
    audio: Optional[str] = Field(default=None, description="Optional audio recording")
class BaseResponse(BaseModel):
    status: str
    message: Optional[str] = None