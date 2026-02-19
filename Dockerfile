FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /home/app/.config/matplotlib

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY . .
RUN pip install --no-cache-dir .
RUN chown -R app:app /app /home/app

ENV HOME=/home/app
ENV MPLCONFIGDIR=/home/app/.config/matplotlib

USER app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
