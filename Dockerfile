FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
RUN chainlit init 2>/dev/null || true

ENV PYTHONPATH=/app/src
ENV OCI_USE_INSTANCE_PRINCIPAL=true

EXPOSE 8000

ENTRYPOINT ["chainlit", "run", "src/ri_agent/app.py", "--host", "0.0.0.0", "--port", "8000"]
