# Conllu-FastApi
docker build . --tag fastapi_app
docker run -p 80:80 fastapi_app



docker run -d -p 8000:8000 -v $(pwd)/data:/app/data fastapi_app
scp -i my-key-pair.pem ubuntu@3.84.57.147:/home/ubuntu/Conllu-FastApi/data/database.db /home/nurtilek/Downloads
