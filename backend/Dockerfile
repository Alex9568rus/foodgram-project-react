FROM python:3.7-slim

LABEL author='Zhbakov A' version=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --upgrade pip

COPY . .

CMD [ "gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]