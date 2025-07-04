from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables, delete_tables
from import_data import start_import_data
from app.routers.sentences import router as sentence_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_tables()
    print("База готова")
    await start_import_data()
    yield
    print("Выключение")
app = FastAPI(lifespan=lifespan)

# Разрешённые источники (указывай фронтенд URL)
origins = [
    "http://localhost:5173",  # Vite React фронтенд
    "https://conllu-editor.vercel.app",   # Альтернативный локальный адрес
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://aitilchi.mooo.com", "https://aitilchi.mooo.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentence_router)