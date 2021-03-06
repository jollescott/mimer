# pull official base image
FROM python:3.7-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN apk update \
    && apk add build-base gcc python3-dev libffi-dev

RUN apk add postgresql-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
RUN pip install ./sana-python

ENV DJANGO_SETTINGS_MODULE mimer.settings.production
RUN python manage.py migrate
RUN python manage.py collectstatic
RUN python manage.py import_questions ./questions.json  --init --count 75
RUN python manage.py sync_sana 
RUN echo "from quiz.models import QuizUser; QuizUser.objects.create_superuser('joel', 'JoLi0125@student.grillska.se', '@GrillskaCool123')" | python manage.py shell; exit 0

# add and run as non-root user
RUN adduser -D mimer
USER mimer

# run gunicorn
CMD gunicorn mimer.wsgi:application --bind 0.0.0.0:$PORT