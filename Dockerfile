FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential libssl-dev

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV BOT_TOKEN=${BOT_TOKEN}

CMD ["python", "main.py"]
