FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./

COPY src ./src

RUN uv sync --frozen --no-dev

EXPOSE 8080

CMD ["sh", "-c", "uv run fastapi run src/ocr_api/main.py --host 0.0.0.0 --port ${PORT:-8080}"]