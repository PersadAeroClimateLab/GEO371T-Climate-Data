FROM python:3.14.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python3"]
