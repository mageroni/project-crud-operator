FROM python:3.13-slim

WORKDIR /action/workspace

# Copy project files
COPY project-operator.py requirements.txt /action/workspace/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Create a .env file from the example if it doesn't exist
RUN if [ ! -f .env ]; then cp .env-example .env; fi

CMD ["/action/workspace/project-operator.py"]
ENTRYPOINT ["python", "-u"]
