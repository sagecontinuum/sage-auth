

# docker build -t waggle/sage-auth .

#ash
# docker run -ti --rm --name sage-auth -v `pwd`/app/:/usr/src/app --entrypoint /bin/ash waggle/sage-auth


#webserver
# docker run -ti --rm --name sage-auth -p 8000:80 --env Globus_Auth_Client_ID="${Globus_Auth_Client_ID}" --env Globus_Auth_Client_Secret="${Globus_Auth_Client_Secret}" waggle/sage-auth


#FROM python:3.8-alpine
#FROM python:3.10-rc-alpine
FROM alpine:3.13

RUN apk update

RUN apk add python3 py3-pip python3-dev
RUN apk add mariadb-connector-c-dev  # needed for mysqlclient to install mysql_config
RUN apk add gcc musl-dev             # needed for mysqlclient
RUN apk add libffi-dev rust cargo    # needed for cryptography
RUN pip install --upgrade pip

WORKDIR /usr/src/app/webapp


COPY requirements.txt ./
RUN pip install -r requirements.txt


COPY app /usr/src/app/

COPY testing-entrypoint.sh /testing-entrypoint.sh
RUN chmod 755 /testing-entrypoint.sh

# PATCH globus.py, insert code at line 12
RUN sed -i "12i\ \ \ \ JWT_ALGORITHMS = ['RS512']" /usr/lib/python*/site-packages/social_core/backends/globus.py

EXPOSE 80
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]