# database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Создаем асинхронный движок и сессию
engine = create_async_engine("sqlite+aiosqlite:///data/database.db", echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)

# Создаем Base для наследования в моделях
Base = declarative_base()

# Избегаем циклического импорта
async def create_tables():
    from app.models import Sentence, Token  # Импортируем модели здесь, чтобы избежать цикличности
    async with engine.begin() as conn:
        # Создаем все таблицы, зарегистрированные в Base
        await conn.run_sync(Base.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        # Удаляем все таблицы
        await conn.run_sync(Base.metadata.drop_all)
