FROM rasa/rasa:3.6.2
USER root
RUN mkdir -p /app/src

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY actions/actions.py /app/actions/actions.py
COPY src/ /app/src
COPY data/motd/motd.yml /app/data/motd/motd.yml

ENV PYTHONPATH "${PYTHONPATH}:/app/src/municipal_info_api"

WORKDIR /app

EXPOSE 5055

# Switch back to non-root to run code
USER 1001

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]
