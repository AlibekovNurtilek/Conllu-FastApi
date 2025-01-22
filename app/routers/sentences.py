from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Sentence
from app.database import new_session
from app.schemas import PaginatedResponse


router = APIRouter()

async def get_paginated_sentences(page: int = 1, size: int = 10):
    # Считаем общее количество предложений
    async with new_session() as session:
        result = await session.execute(select(Sentence))
        sentences = result.scalars().all()  # Получаем все предложения

        total_sentences = len(sentences)  # Используем len() для подсчета количества
        # Вычисляем количество страниц
        pages = (total_sentences + size - 1) // size

        # Проверяем корректность страницы
        if page > pages:
            raise HTTPException(status_code=404, detail="Page not found")

        # Получаем нужную страницу
        offset = (page - 1) * size
        result = await session.execute(select(Sentence).offset(offset).limit(size))
        sentences = result.scalars().all()

        return {
            "total": total_sentences,
            "pages": pages,
            "page": page,
            "size": size,
            "items": [sentence for sentence in sentences]
        }

@router.get("/sentences", response_model=PaginatedResponse)
async def get_sentences(
    page: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, le=100)
):
    return await get_paginated_sentences( page, size)
