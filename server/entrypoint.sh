#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py shell -c 'from djangoapp.populate import initiate; initiate()'
python manage.py collectstatic --noinput
exec "$@"
