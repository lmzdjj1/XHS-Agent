FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY api_server.py cli.py xhs_workflow.py ./
COPY xhs_agent ./xhs_agent
COPY static ./static
COPY examples ./examples
COPY "XHS Content Agent宣传封面图.png" ./

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
