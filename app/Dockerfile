FROM python:3.7-alpine
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app