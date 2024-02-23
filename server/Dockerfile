FROM python:3.11.7-slim

WORKDIR /server

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=/server/standalone.py
WORKDIR /

CMD ["python3","-m","flask","run","--host","0.0.0.0","--port","5000","--no-reload","--with-threads"]