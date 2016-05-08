for docker dev version

create .env file

```
DEBUG=True
SECRET_KEY=
STATIC_ROOT=/app/static/
STATIC_URL=static/
MEDIA_ROOT=/app/media/
MEDIA_URL=media/
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DATABASE_URL=postgres://user:password@db/fablabadmin
RECAPTCHA_PRIVATE_KEY = 'your private key'
RECAPTCHA_PUBLIC_KEY = 'your public key'
CCVSHOP_DOMAIN = 'full url to securearea url'
CCVSHOP_PRIVATE_KEY = 'your private key'
CCVSHOP_PUBLIC_KEY = 'your public key'
``` 

```
 docker-compose build
 docker-compose up -d
 docker-compose run web python manage.py migrate
 docker-compose run web python manage.py createsuperuser
 docker-compose run web python manage.py collectstatic
```

dev translations inside app folders
django-admin makemessages
django-admin compilemessages 