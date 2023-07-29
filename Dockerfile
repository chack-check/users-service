FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /src

RUN pip install -U poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /src/

RUN poetry install --no-interaction --no-ansi

COPY app/ /src/app
COPY templates/ /src/templates

ENTRYPOINT [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]