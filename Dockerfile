FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput || true

CMD sh -c 'python manage.py migrate && python manage.py regeocode_parcels --apply && gunicorn --bind 0.0.0.0:$PORT config.wsgi:application'
