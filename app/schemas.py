from pydantic import BaseModel
from typing import List, Optional


#для получения список предложений
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

#для получания предложения с токенами
class TokenBase(BaseModel):
    id: int
    form: str
    lemma: Optional[str] = None
    pos: Optional[str] = None
    xpos: Optional[str] = None
    feats: Optional[dict] = None
    head: Optional[int] = None
    deprel: Optional[str] = None
    misc: Optional[str] = None

    class Config:
        orm_mode = True

#для обновление

class SentenceWithTokens(BaseModel):
    id: int
    text: str
    is_corrected: int
    tokens: List[TokenBase]

    class Config:
        orm_mode = True


class TokenUpdate(BaseModel):
    id: int
    form: Optional[str]
    lemma: Optional[str]
    pos: Optional[str]
    xpos: Optional[str]
    feats: Optional[dict]
    head: Optional[int]
    deprel: Optional[str]
    misc: Optional[str]

class SentenceUpdate(BaseModel):
    text: Optional[str]



#для создание
class TokenCreate(BaseModel):
    form: str
    lemma: str
    pos: str
    xpos: str
    feats: Optional[dict] = None
    head: int
    deprel: str
    misc: Optional[str] = None

class SentenceCreate(BaseModel):
    text: str
    is_corrected: int
    tokens: List[TokenCreate]

class SentenceResponse(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True
