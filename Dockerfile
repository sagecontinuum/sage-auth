

# docker build -t sage/sage-ui .

#ash
# docker run -ti --rm --name sage-ui -v `pwd`/app/:/usr/src/app --entrypoint /bin/ash sage/sage-ui


#webserver
# docker run -ti --rm --name sage-ui -p 8000:80 --env Globus_Auth_Client_ID="${Globus_Auth_Client_ID}" --env Globus_Auth_Client_Secret="${Globus_Auth_Client_Secret}" sage/sage-ui


FROM python:3.8-alpine 


RUN apk update 
   
WORKDIR /usr/src/app/webapp


COPY requirements.txt ./
RUN pip install -r requirements.txt


COPY app /usr/src/app/

EXPOSE 80
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]