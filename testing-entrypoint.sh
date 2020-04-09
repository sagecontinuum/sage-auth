#!/bin/sh

## do not use for production ! ## 

while [ $(nc -z db 3306 ; echo $?) != 0 ] ; do
 echo "wait..."
 sleep 2
done
set -x
#python manage.py migrate --fake # Reset the migrations for the "built-in" apps
#python manage.py makemigrations webapp
python manage.py migrate 

./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('test', 'test@example.com', 'test')" 
./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('sage-api-server', 'test@example.com', 'test')" 
./manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('root', 'admin@myproject.com', 'root')"


python manage.py runserver 0.0.0.0:80