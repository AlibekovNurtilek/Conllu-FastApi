# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Скопируем файлы проекта в контейнер
COPY . /app

# Установим зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Пробросим порт, который будет использовать FastAPI (по умолчанию 8000)
EXPOSE 8000

# Запуск приложения с помощью Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
