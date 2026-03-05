FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app.py /app

EXPOSE 5000

RUN adduser -D appuser
USER appuser

ENTRYPOINT ["flask"]

CMD ["--app", "app.py", "run", "--host", "0.0.0.0", "--port", "5000"]
