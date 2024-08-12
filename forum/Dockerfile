FROM python:3.10.6-slim

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; from account.models import Profile; user = User.objects.get(username='admin') if User.objects.filter(username='admin').exists() else User.objects.create_superuser('admin', 'admin@example.com', 'adminadmin'); Profile.objects.create(user=user)" \
    && python manage.py collectstatic --noinput \
    && gunicorn forum.wsgi:application --bind 0.0.0.0:8000 --log-level info