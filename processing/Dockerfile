FROM python:3.10-slim

WORKDIR /opt/app

COPY app/ /opt/app/
COPY requirements.txt .
COPY entrypoint.sh /entrypoint.sh

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
