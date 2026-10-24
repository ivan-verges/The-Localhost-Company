FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic

COPY agent.py /app/agent.py

EXPOSE 4000

CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "4000"]
