# models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.database import Base  # Импортируем Base, который теперь корректно инициализирован

class Sentence(Base):
    __tablename__ = 'sentences'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)  # Текст предложения
    is_corrected = Column(Integer, default=0)  # 0 - не исправлено, 1 - исправлено
    
    tokens = relationship("Token", back_populates="sentence")

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    # Новое поле для хранения индекса токена в предложении, поддерживает диапазоны
    token_index = Column(String, index=True)  # Индекс токена в предложении (например, "3-5" или "1")
    form = Column(String, index=True)  # Форма токена (например, слово)
    lemma = Column(String)  # Лемма токена
    pos = Column(String)  # Часть речи
    xpos = Column(String)  # Точная часть речи
    feats = Column(JSON)  # Характеристики токена (например, морфологические признаки)
    head = Column(Integer, ForeignKey("tokens.id"))  # Ссылка на головной токен (ID)
    deprel = Column(String)  # Тип зависимости
    misc = Column(String)  # Дополнительные комментарии
    sentence_id = Column(Integer, ForeignKey("sentences.id"))
    sentence = relationship("Sentence", back_populates="tokens")
    

    head_token = relationship("Token", remote_side=[id])


