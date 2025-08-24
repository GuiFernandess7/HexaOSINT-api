from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class TargetTextSchemaResponse(BaseModel):
    """Schema for the response of target text search."""

    title: str
    link: str
    snippet: str
    source: str


class ListTargetsResponse(BaseModel):
    """Schema for the list of target text search results."""

    message: str = Field(default="Success")
    data: List[Any] = Field(default_factory=list)
    total: int = Field(default=0)


class TargetImageSchemaResponse(BaseModel):
    guid: str
    score: int
    url: str
    snippet: Optional[str]

    class Config:
        extra = "allow"


class ListTargetsImageResponse(BaseModel):
    """Schema for the list of target image search results."""

    message: str = Field(default="Success")
    data: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = Field(default=0)
    progress: Optional[int] = Field(default=None)


class TargetSendImageSchemaResponse(BaseModel):
    """Schema for sending target image data."""

    status: str
    message: str
    id_search: Optional[str] = None
