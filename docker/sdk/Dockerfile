FROM rasa/rasa-sdk:3.4.0
USER root
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --default-timeout=100 islenska==0.4.5
RUN pip install --no-cache-dir requests==2.26.0

RUN mkdir -p /app/src
COPY actions/actions.py /app/actions/actions.py
COPY src/ /app/src

ENV PYTHONPATH "${PYTHONPATH}:/app/src/municipal_info_api"

WORKDIR /app

EXPOSE 5055

# Switch back to non-root to run code
USER 1001

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]
