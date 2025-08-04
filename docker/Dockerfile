FROM python:3.12.11-slim
LABEL authors="agrubio"

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

USER nonroot

COPY requirements.txt .
COPY src .
RUN python -m pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "src"]