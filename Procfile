web: gunicorn wsgi:app --log-file - --chdir ./app
release: python manage.py db upgrade -d app/migrations/
