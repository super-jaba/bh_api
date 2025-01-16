FROM python:3.11-slim

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

WORKDIR /src

CMD ["python", "main.py"]