from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Sentence, Token
from app.database import new_session
from app.schemas import PaginatedResponse, SentenceWithTokens, SentenceUpdate, TokenUpdate, SentenceCreate, SentenceResponse


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


@router.get("/sentences/{sentence_id}", response_model=SentenceWithTokens)
async def get_sentence_by_id(sentence_id: int):
    async with new_session() as session:
        # Получаем предложение с токенами по ID
        result = await session.execute(
            select(Sentence)
            .where(Sentence.id == sentence_id)
            .options(
                selectinload(Sentence.tokens)
            )
        )
        sentence = result.scalars().first()
        if not sentence:
            raise HTTPException(status_code=404, detail="Sentence not found")

        return sentence

@router.put("/sentences/{sentence_id}")
async def update_sentence_by_id(
    sentence_id: int, 
    updated_sentence: SentenceUpdate, 
    updated_tokens: list[TokenUpdate]
):  
    async with new_session() as session:
        # Получаем предложение по ID
        result = await session.execute(
            select(Sentence).where(Sentence.id == sentence_id).options(selectinload(Sentence.tokens))
        )
        sentence = result.scalars().first()

        if not sentence:
            raise HTTPException(status_code=404, detail="Sentence not found")

        # Обновляем данные предложения
        sentence.text = updated_sentence.text if updated_sentence.text else sentence.text
        sentence.is_corrected = 1
        
        # Сохраняем список id токенов, которые должны остаться
        updated_token_ids = [token_data.id for token_data in updated_tokens if token_data.id]

        # Удаляем токены, которых нет в списке обновленных токенов
        tokens_to_delete = [token for token in sentence.tokens if token.id not in updated_token_ids]
        for token in tokens_to_delete:
            sentence.tokens.remove(token)
        
        # Обновляем или добавляем новые токены
        for token_data in updated_tokens:
            token = next((t for t in sentence.tokens if t.id == token_data.id), None)
            if token:
                # Обновляем существующие токены
                token.form = token_data.form if token_data.form else token.form
                token.lemma = token_data.lemma if token_data.lemma else token.lemma
                token.pos = token_data.pos if token_data.pos else token.pos
                token.xpos = token_data.xpos if token_data.xpos else token.xpos
                if token_data.feats is not None:
                    token.feats = token_data.feats
                token.head = token_data.head if token_data.head is not None else token.head
                token.deprel = token_data.deprel if token_data.deprel else token.deprel
                token.misc = token_data.misc if token_data.misc else token.misc
            else:
                # Если токен с таким ID не найден в предложении, добавляем новый
                new_token = Token(**token_data.model_dump(), sentence_id=sentence.id)
                sentence.tokens.append(new_token)

        # Сохраняем изменения в базе данных
        await session.commit()

        return {"message": "Sentence and tokens updated successfully"}


@router.post("/sentences", response_model=SentenceResponse)
async def create_sentence(
    request: SentenceCreate
):
    # Создаем новое предложение
    new_sentence = Sentence(
        text=request.text,
        is_corrected=request.is_corrected
    )
    
    # Добавляем токены
    for token_data in request.tokens:
        new_token = Token(
            form=token_data.form,
            lemma=token_data.lemma,
            pos=token_data.pos,
            xpos=token_data.xpos,
            feats=token_data.feats,
            head=token_data.head,
            deprel=token_data.deprel,
            misc=token_data.misc,
            sentence=new_sentence  # Связываем токен с предложением
        )
        new_sentence.tokens.append(new_token)
    async with new_session() as session:
        # Добавляем предложение и токены в базу данных
        session.add(new_sentence)
        await session.commit()
        
        # Возвращаем созданное предложение
        return {"id": new_sentence.id, "text": new_sentence.text}
    



@router.get("/tokens/clean_person_in_feats")
async def clean_person_in_feats():
    async with new_session() as session:
        # Получаем все токены, где pos == NOUN, PROPN, PRON
        result = await session.execute(
            select(Token).where(Token.pos.in_(['NOUN', 'PROPN', 'PRON']))
        )
        tokens = result.scalars().all()

        if not tokens:
            raise HTTPException(status_code=404, detail="No tokens found with the specified POS")

        # Обрабатываем каждый токен
        for token in tokens:
            if token.feats and "Person" in token.feats:

                token.feats = {key: value for key, value in token.feats.items() if key != "Person"}
                session.add(token)

        await session.flush()       
        await session.commit()
        return {"message": "Person field removed from feats for relevant tokens"}