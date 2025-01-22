from pydantic import BaseModel
from typing import List

class SentenceResponse(BaseModel):
    id: int
    text: str
    is_corrected: int

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    total: int
    pages: int
    page: int
    size: int
    items: List[SentenceResponse]
