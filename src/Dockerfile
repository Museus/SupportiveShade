FROM python:3-slim

# Use Bash as shell
SHELL ["/bin/bash", "-c"]

# Create deploy user
RUN useradd -ms /bin/bash deploy

# silence Dialog TERM not set errors in apt-get install
ENV DEBIAN_FRONTEND noninteractive

# Install all system requirements
COPY ./system-requirements.txt ./system-requirements.txt
RUN apt-get update && apt-get install -y $(cat ./system-requirements.txt)

# Install all Python requirements
COPY ./python-requirements.txt ./python-requirements.txt
RUN python3 -m venv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --ignore-installed -r python-requirements.txt

# Set context for entrypoint
WORKDIR /app

# Copy application
COPY ./app/* .

# Set metadata as specified by https://github.com/opencontainers/image-spec/blob/main/annotations.md
ARG BUILD_TIMESTAMP="unknown"
ARG BUILD_VERSION="unknown"

LABEL org.opencontainers.image.created="${BUILD_TIMESTAMP}"
LABEL org.opencontainers.image.authors="Museus <museus@proton.me>"
LABEL org.opencontainers.image.url=""
LABEL org.opencontainers.image.documentation=""
LABEL org.opencontainers.image.source=""
LABEL org.opencontainers.image.version="v${BUILD_VERSION}"
LABEL org.opencontainers.image.vendor=""
LABEL org.opencontainers.image.title=""
LABEL org.opencontainers.image.description=""

ENTRYPOINT ["bash", "-c", "./start.sh"]