FROM 3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

ENV PYTHONUNBUFFERED=1 
CMD ["python", "main.py"]
