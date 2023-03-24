FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD [ "uvicorn", "sql_app.main:app", "--reload", "--host", "0.0.0.0" ]
