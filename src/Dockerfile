FROM python:3-slim

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /var/lib/supportive_shade

COPY ./system-requirements.txt ./system-requirements.txt
RUN apt-get update && apt-get install -y $(cat ./system-requirements.txt)

COPY ./python-requirements.txt ./python-requirements.txt
RUN python3 -m venv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r python-requirements.txt

RUN python3 -m pip install -r ./python-requirements.txt

COPY ./app /opt/supportive_shade

WORKDIR /opt/supportive_shade

ARG BUILD_TIMESTAMP="unknown"

LABEL org.opencontainers.image.created="${BUILD_TIMESTAMP}}"
LABEL org.opencontainers.image.authors="Museus <museus@proton.me>"
LABEL org.opencontainers.title="Supportive Shade"
LABEL org.opencontainers.image.description="Discord bot for the Hades Speedrunning discord server"

ENTRYPOINT [ "bash", "-c", "./start.sh" ]

