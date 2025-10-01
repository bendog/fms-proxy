FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ADD . /app
RUN uv build

###
# Run Environment
###

FROM python:3.13-slim

COPY --from=builder /app/dist /app
WORKDIR /app
RUN ls

RUN pip install *.whl

ENV OUTLOOK_PATH_MUST_CONTAIN="owa/calendar/"
EXPOSE 8000

ADD ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
