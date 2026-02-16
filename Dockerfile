FROM python:3.10-slim

WORKDIR /App
COPY . /App

RUN apt-get update && apt-get install -y awscli
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python3", "App.py"]
