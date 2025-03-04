# Используем официальный образ Python (slim для минимального размера)
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Убедимся, что у нас свежая версия pip и установим зависимости
RUN pip install --no-cache-dir --upgrade pip

# Копируем только файлы с зависимостями для кеширования слоёв
COPY requirements.txt .

# Устанавливаем зависимости перед копированием всего кода (ускоряет сборку)
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем весь проект в контейнер
COPY . .

# Создаём папку для базы данных (если её нет)
RUN mkdir -p /app/data

# Открываем порт 8000 (для FastAPI)
EXPOSE 8000

# Указываем команду запуска (Uvicorn + FastAPI)
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
