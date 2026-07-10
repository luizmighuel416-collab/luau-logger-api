FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl unzip
RUN curl -L https://github.com/luau-lang/luau/releases/latest/download/luau-ubuntu.zip -o luau.zip && \
    unzip luau.zip && mv luau /usr/local/bin/ && chmod +x /usr/local/bin/luau

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
