## Build venv
FROM python:3.10 AS build-python

WORKDIR /etc/swift_demo

RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH /root/.local/bin:$PATH

RUN poetry config virtualenvs.in-project true

COPY backend/pyproject.toml backend/poetry.lock* ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

ENV PATH /etc/swift_demo/.venv/bin:$PATH
ENV PYTHONPATH /etc/swift_demo

COPY . /etc/swift_demo/

## Build frontend app
FROM node:18 as build-node

ARG VITE_BUILD_MODE
ENV VITE_API_URL /api
ENV NODE_ENV production

WORKDIR /app
COPY frontend/package*.json /app/
COPY frontend/yarn.lock /app/

RUN yarn

COPY ./frontend /app/

RUN yarn build

## Build runtime image
FROM python:3.10-slim@sha256:42d13fdfccf5d97bd23f9c054f22bde0451a3da0a7bb518bcd95fec6be89b50d as prod

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set environment variables
ARG GCLOUD_PROJECT_ID

ENV ENVIRONMENT production
ENV CERTIFICATE_PATH /etc/swift_demo/secrets/certificate/certificate.pem
ENV PRIVATE_KEY_PATH /etc/swift_demo/secrets/private-key/private-key.pem
ENV GCLOUD_PROJECT_ID $GCLOUD_PROJECT_ID

COPY --from=build-python /etc/swift_demo/.venv /etc/swift_demo/.venv
ENV PATH /etc/swift_demo/.venv/bin:$PATH
ENV PYTHONPATH /etc/swift_demo

COPY --from=build-node /app/dist /etc/swift_demo/static

WORKDIR /etc/swift_demo
COPY backend/swift_demo /etc/swift_demo/swift_demo

CMD uvicorn swift_demo.main:app --host 0.0.0.0 --port 8000
