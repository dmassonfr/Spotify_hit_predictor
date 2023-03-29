FROM python:3.10.6-buster

WORKDIR /prod

# Install requirements
COPY requirements_prod.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY inference-api.py inference-api.py
COPY model model

CMD uvicorn inference-api:inference --host 0.0.0.0 --port $PORT