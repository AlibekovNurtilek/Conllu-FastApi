import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Sentence, Token
import asyncio

# Создаем асинхронный движок и сессию
DATABASE_URL = "sqlite+aiosqlite:///data/database.db"
engine = create_async_engine(DATABASE_URL, echo=False)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def convert_to_conllu(session: AsyncSession, output_file: str):
    async with session.begin():
        result = await session.execute(select(Sentence).options(selectinload(Sentence.tokens)))
        sentences = result.scalars().all()

    conllu_lines = []
    for sentence in sentences:
        conllu_lines.append(f"# sent_id = {sentence.id}")
        conllu_lines.append(f"# text = {sentence.text}")
        
        tokens = sentence.tokens
        
        def token_sort_key(token):
            if "-" in token.token_index:
                start, end = map(int, token.token_index.split("-"))
                return (start - 1, start + 0.5)  # Ставим MWT между x-1 и x
            return (int(token.token_index),)
        
        sorted_tokens = sorted(tokens, key=token_sort_key)
        
        for token in sorted_tokens:
            conllu_lines.append(await format_token_line(token))
        
        conllu_lines.append("")  # Пустая строка между предложениями
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(conllu_lines))
    
    print(f"Data successfully exported to {output_file}!")

async def format_token_line(token):
    """Форматирует строку для CoNLL-U."""
    upos_fixed = await fix_upos(token.pos)
    xpos_fixed = await fix_xpos(token.pos, token.xpos)
    feats_formatted = await format_feats(token.feats)
    return (
        f"{token.token_index}\t{token.form}\t{token.lemma}\t{upos_fixed}\t"
        f"{xpos_fixed}\t{feats_formatted}\t{token.head if token.head is not None else 0}\t"
        f"{token.deprel if token.deprel is not None else '_'}\t_\t{token.misc if token.misc is not None else '_'}"
    )

async def fix_upos(upos):
    """Если тег кастомный, заменяем UPOS на X."""
    if upos is None:
        return "_"
    custom_tags = {"ttsoz", "etsoz", "issoz", "assoz", "ttsssoz", "atooch", "ktooch"}
    return "X" if upos.lower() in custom_tags else upos.upper()

async def fix_xpos(upos, xpos):
    """Приводим XPOS к нижнему регистру. Если UPOS стандартный, копируем его в XPOS."""
    standard_upos_tags = {"NOUN", "PROPN", "ADJ", "PRON", "NUM", "VERB", "AUX", "ADV", "CCONJ", "SCONJ", "PART", "INTJ", "ADP", "DET", "PUNCT", "SYM"}
    if upos in standard_upos_tags:
        return upos.lower()
    return xpos.lower() if xpos else "_"

async def format_feats(feats):
    """Преобразование FEATS из JSON в строку формата CoNLL-U."""
    if not feats or feats == "_":
        return "_"
    
    if isinstance(feats, str):
        feats = json.loads(feats)
    
    formatted_feats = [f"{key}={value}" for key, value in feats.items()]
    return "|".join(formatted_feats) if formatted_feats else "_"

async def start_export_data():
    async with new_session() as session:
        await convert_to_conllu(session, "data/output.conllu")

if __name__ == "__main__":
    asyncio.run(start_export_data())
