FROM python:3.8.6-slim
RUN apt-get update && apt-get -y install postgresql-client
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
COPY . .
CMD python main.py
