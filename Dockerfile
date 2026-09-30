FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY run.py .

ENV PORT=5503
ENV FLASK_DEBUG=false

EXPOSE 5503

CMD ["python", "run.py"]
