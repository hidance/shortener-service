FROM python:3.10-alpine

WORKDIR /app 

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN adduser -D appuser

COPY . .

RUN chown -R appuser /app

USER appuser


EXPOSE 5000

CMD ["python", "app.py"]
