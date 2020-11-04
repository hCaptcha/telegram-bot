web: gunicorn wsgi:app --log-file - --chdir ./app

// commenting this out due to https://github.com/hCaptcha/telegram-bot/issues/25
// release: python manage.py db upgrade -d app/migrations/
