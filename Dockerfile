FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages


# Make entrypoint executable
COPY entrypoint.sh .
COPY main.py .
RUN chmod +x entrypoint.sh

# Override the ollama entrypoint
ENTRYPOINT []
CMD ["/bin/bash", "./entrypoint.sh"]