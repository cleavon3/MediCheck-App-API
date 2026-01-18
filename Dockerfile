FROM python:3.9-alpine3.13
LABEL maintainers="skilldigitalsolutions.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000 

<<<<<<< HEAD
ARG DEV=false

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    addgroup --system django && \
    adduser --system --ingroup django django-user && \
    chown -R django-user:django /py /app

ENV PATH="/py/bin:$PATH"

USER django-user
=======
ARG DEV=true
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
        fi && \
    rm -rf /tmp && \ 
    adduser \
       --disabled-password\
       --no-create-home \
       django-user

ENV PATH="/py/bin:$PATH"

USER django-user
>>>>>>> 369e8ce0160255d438b75c1fc3a65773cce11eae
