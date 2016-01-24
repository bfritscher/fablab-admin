for docker dev version

create .env file

```
DEBUG=True
STATIC_ROOT=/.../static/
MEDIA_ROOT=
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DATABASE_URL=postgres://user:password@db/fablabadmin
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