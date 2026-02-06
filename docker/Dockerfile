# =========================
# Builder
# =========================
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Copiar solo archivos para deps
COPY pyproject.toml uv.lock ./
COPY README.md .

# Instalar dependencias + proyecto, directo en el Python del sistema
RUN uv sync --no-dev

COPY src/ src/
COPY ./conf ./conf

EXPOSE 5000

CMD ["uv", "run", "python", "src"]
