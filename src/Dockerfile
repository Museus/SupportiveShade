FROM python:3-slim

WORKDIR /opt/supportive_shade

RUN python3 -m pip install discord-py

COPY ./app/* .
CMD ["python3", "main.py"]

