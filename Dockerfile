

# docker build -t sagecontinuum/sage-ui .

#ash
# docker run -ti --rm --name sage-ui -v `pwd`/app/:/usr/src/app --entrypoint /bin/ash sagecontinuum/sage-ui


#webserver
# docker run -ti --rm --name sage-ui -p 8000:80 --env Globus_Auth_Client_ID="${Globus_Auth_Client_ID}" --env Globus_Auth_Client_Secret="${Globus_Auth_Client_Secret}" sagecontinuum/sage-ui


#FROM python:3.8-alpine
FROM python:3.10-rc-alpine

RUN apk update

RUN apk add mariadb-connector-c-dev  # needed for mysqlclient to install mysql_config
RUN apk add gcc musl-dev             # needed for mysqlclient
RUN apk add libffi-dev               # needed for cryptography
RUN pip install --upgrade pip

WORKDIR /usr/src/app/webapp


COPY requirements.txt ./
RUN pip install -r requirements.txt


COPY app /usr/src/app/

COPY testing-entrypoint.sh /testing-entrypoint.sh
RUN chmod 755 /testing-entrypoint.sh

EXPOSE 80
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]