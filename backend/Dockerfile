FROM python:3.11-slim

WORKDIR /app

COPY api.py .
RUN pip install --no-cache-dir fastapi uvicorn newspaper4k lxml_html_clean

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
