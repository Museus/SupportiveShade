FROM python:3-slim

WORKDIR /opt/supportive_shade

RUN python3 -m pip install discord-py pydantic pydantic_settings[toml]

COPY ./app/* .
CMD ["python3", "main.py"]

