FROM rasa/rasa-sdk:3.6.1
USER root
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --default-timeout=100 islenska==0.4.7
RUN pip install --no-cache-dir pyyaml==6.0
RUN pip install --no-cache-dir requests==2.31.0

RUN mkdir -p /app/src
COPY actions/actions.py /app/actions/actions.py
COPY src/ /app/src
COPY data/motd/motd.yml /app/data/motd/motd.yml

ENV PYTHONPATH "${PYTHONPATH}:/app/src/municipal_info_api"

WORKDIR /app

EXPOSE 5055

# Switch back to non-root to run code
USER 1001

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]
