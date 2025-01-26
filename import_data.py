import logging
from conllu import parse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Sentence, Token
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Создаем асинхронный движок и сессию
engine = create_async_engine("sqlite+aiosqlite:///data/database.db", echo=False)
new_session = async_sessionmaker(engine, expire_on_commit=False)



async def load_conllu_to_db(file_path: str, session: AsyncSession):
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    sentences = parse(data)

    for sent in sentences:
        sentence_text = " ".join([token["form"] for token in sent])
        db_sentence = Sentence(text=sentence_text, is_corrected=0)
        session.add(db_sentence)
        await session.flush()  # Получаем ID для предложения

        for token in sent:
            db_token = Token(
                form=token["form"],
                lemma=token.get("lemma"),
                pos=token.get("upostag"),
                xpos=token.get("xpostag"),
                head=token.get("head"),
                deprel=token.get("deprel"),
                misc=str(token.get("misc", {})),
                feats=token.get("feats"),
                sentence_id=db_sentence.id
            )
            session.add(db_token)

    await session.commit()
    print(f"Data from {file_path} successfully imported!")


async def check_data_exists(session: AsyncSession) -> bool:
    # Проверяем, есть ли хотя бы одна запись в таблице Sentence
    result = await session.execute(select(Sentence).limit(1))
    sentence_exists = result.scalar() is not None

    # Если в таблице Sentence есть данные, проверяем для Token
    if sentence_exists:
        result = await session.execute(select(Token).limit(1))
        token_exists = result.scalar() is not None
        return token_exists

    return False

async def start_import_data():
    async with new_session() as session:
        if await check_data_exists(session):
            print("Data already exists in the database. Skipping import.")
            return
        await load_conllu_to_db("data/mydata.conllu", session)


