# Pull base image
FROM python:3.12.0rc2-bookworm

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN apt-get update && apt-get install -y gettext && apt-get install -y vim

# Copy project
COPY . /app
COPY ./entrypoint.sh /

ENTRYPOINT ["sh", "/entrypoint.sh"]