FROM python:3.10-slim
WORKDIR /App
COPY . /App

RUN apt-get update && apt-get install -y awscli

RUN apt-get update && pip install -r requirements.txt
CMD ["python3", "App.py"]