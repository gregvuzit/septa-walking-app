FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/app"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./scripts/start.sh /
RUN chmod +x /start.sh

CMD ["/start.sh"]