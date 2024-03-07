# app/Dockerfile

FROM python:3.9-slim

WORKDIR /root/ProctorPal

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ThatRandomSkid/ProctorPal.git .

RUN pip3 install -r requirements.txt

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "ProctorPal.py", "--server.port=8502", "--server.enableCORS=false", "--server.enableWebsocketCompression=false", "--server.address=0.0.0.0"]