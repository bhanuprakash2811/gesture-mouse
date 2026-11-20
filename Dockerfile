FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libasound2 \
        libasound2-plugins \
        libgl1 \
        libglib2.0-0 \
        libtk8.6 \
        portaudio19-dev \
        xauth \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY src/ src/
COPY scripts/ scripts/
COPY tests/ tests/

CMD ["python", "-m", "scripts.maintenance.verify_installation"]
