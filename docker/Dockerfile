FROM python:3.12.11-slim
LABEL authors="agrubio"

COPY requirements.txt .
COPY src .
RUN python -m pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "src"]
