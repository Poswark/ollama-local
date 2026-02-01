FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages 

COPY . .

## Offline para server sin internet
RUN ollama serve & \
    sleep 10 && \
    ollama pull gemma:2b && \
    pkill ollama

ENTRYPOINT []

CMD /bin/ollama serve & sleep 5 && python3 main.py