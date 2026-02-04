FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libharfbuzz-subset0 \
        libglib2.0-0 \
        libgobject-2.0-0 \
        libffi-dev \
        libjpeg-dev \
        libopenjp2-7-dev && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 3000 8080

CMD ["python", "phishforge/dashboard/app.py"]
