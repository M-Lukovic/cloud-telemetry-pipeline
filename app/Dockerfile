FROM python:3.10-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test

COPY requirements-dev.txt ./

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY main.py telemetry.py test_main.py ./

CMD ["python", "-m", "pytest", "-p", "no:cacheprovider"]


FROM base AS runtime

RUN addgroup --system --gid 10001 appgroup \
    && adduser --system --uid 10001 --ingroup appgroup appuser

COPY --chown=appuser:appgroup main.py telemetry.py ./

USER 10001:10001

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "main:app"]
