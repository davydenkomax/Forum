FROM python:3.10.6-slim

WORKDIR /app

COPY . /app/

RUN cd ..
RUN ls
RUN slepp 10
RUN chmod +x /scripts/wait-for-it.sh
RUN cd forum
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminadmin')" \
    && python manage.py collectstatic --noinput \
    && gunicorn forum.wsgi:application --bind 0.0.0.0:8000 --log-level info