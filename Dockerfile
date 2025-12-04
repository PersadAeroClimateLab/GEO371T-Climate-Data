FROM quay.io/jupyter/base-notebook:latest

WORKDIR /work

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8888
EXPOSE 8787