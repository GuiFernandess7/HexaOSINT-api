from pydantic import BaseModel, Field
from typing import Optional, List

from enums.target_type import TargetType
from enums.search_type import SearchEnum
from enums.country_type import ContryEnum
from uuid import UUID
from enums.engine_type import EngineEnum

from pydantic import BaseModel, validator
from datetime import datetime
from typing import List


class TargetTextSearchSchema(BaseModel):
    name: str
    type: TargetType
    categories: List[str] = Field(default_factory=list)
    domain: Optional[dict] = Field(default=None)
    country: ContryEnum = Field(default=ContryEnum.BRAZIL)
    search_type: SearchEnum = Field(default=SearchEnum.GOOGLE_SEARCH)
    search_engine: EngineEnum = Field(default=EngineEnum.GOOGLE)

    @validator("categories", each_item=True)
    def check_categories(cls, v):
        ALLOWED_CATEGORIES = {"social", "files", "logs"}
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Invalid Category: {v}")
        return v

    @validator("categories")
    def check_not_empty(cls, v):
        if not v:
            raise ValueError("categories list must not be empty")
        return v


class TargetImageSearchSchema(BaseModel):
    id_search: str
    demo: bool = False


class TargetImageSendSchema(BaseModel):
    image_file: str


class CreateScanSchema(BaseModel):
    user_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    query: str
    engine: str
    search_type: str
    status: str
    image_metadata: dict
