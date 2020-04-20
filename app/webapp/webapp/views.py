from django.shortcuts import render
from django.http import HttpResponse
import json
from webapp.models import Token
import secrets

from django.utils import timezone
import pytz
from datetime import datetime, timedelta
import string 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status


from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils.dateformat import format as dformat



def home(request):
    uuid = None
    access_token = None
    refresh_token = None
    if request.user.is_authenticated:
        try:
            globus_user = request.user.social_auth.get(provider='globus')
        except:
            uuid = 'some uuid'
            
            access_token = 'access_token'
            refresh_token = 'refresh_token'
        else:
            uuid = globus_user.uid
            social = request.user.social_auth
            access_token = social.get(provider='globus').extra_data['access_token']
            refresh_token = social.get(provider='globus').extra_data['refresh_token']
       
           

    return render(request,
                  'home.html',
                  {'uuid': uuid,
                  'access_token': access_token,
                  'refresh_token': refresh_token})



def token(request):

    if request.method == 'GET':
        
        #request_data = json.load(request.raw_post_data)
        # do something
        print("token here", flush=True)
        response_data = {}

        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)

        
        alphabet = string.ascii_uppercase + string.digits
        tokenValue = ''.join(secrets.choice(alphabet) for i in range(20))

        expires = timezone.now() + timedelta(days=90)  

        user_uuid = None
        try:
            user_uuid = request.user.social_auth.get(provider='globus').uid
        except:
            # native Django user, this is mostly for testinf purposes
            username = request.user.username
            user_uuid = username
        
       
        if user_uuid == None:
            return HttpResponse("user_uuid is empty", status=500)

        tobject = Token.objects.create(user=user_uuid, tokenValue=tokenValue, expires=expires, scope="default")
        
        
        response_data['token'] = tobject.tokenValue
        

        response_data['user_uuid'] = user_uuid
        response_data['expires'] = "{}/{}/{}".format(expires.month,expires.day,expires.year)
       
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    pass



# Token introspection API
# see https://www.oauth.com/oauth2-servers/token-introspection-endpoint/

class TokenInfo(APIView):
    

    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    #permission_classes = [ AllowAny ]


    def get(self, request, format=None):
        # example: curl -H 'Accept: application/json; indent=4' -u root:root localhost:8000/token_info/
        
        return Response("hello world")

    
    def post(self, request, format=None):
        
        # curl -X POST -H 'Accept: application/json; indent=4' -d 'token=abc' -u root:root localhost:8000/token_info/
        # curl -X POST -H 'Accept: application/json; indent=4' -d 'token=abc' -u sage-api-user:test localhost:8000/token_info/
        
        #return Response("post worked")

        # TODO do this via token permission
        if request.user.username != "sage-api-server":
           content = {'error': 'StatusUnauthorized ({})'.format(request.user.username)}
           return Response(content, status=status.HTTP_401_UNAUTHORIZED) 
       

        data=request.data # is a QueryDict 
       
        token = data.get("token", "")

        try:
            tobject = Token.objects.get(tokenValue=token)
        except Token.DoesNotExist:
            content = {'error': 'token not found'}
            return Response(content, status=status.HTTP_410_GONE )

        if tobject == None:
            content = {'error': 'tobject is empty'}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        expires = tobject.expires

        if expires == None:
            content = {'error': 'expires is empty'}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if timezone.now() > expires:
            content = {'error': 'token expired ({})'.format(str(expires))}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        #user_uuid = None
        #try:
        #    user_uuid = request.user.social_auth.get(provider='globus').uid
        #except:
        #    # native Django user, this is mostly for testing purposes
        #    username = request.user.username
        #    user_uuid = username

        scope = tobject.scope
        user = tobject.user

        unix_expires = int(dformat(expires, 'U'))

        #return Response("valid: "+tobject.user)
        content =      {
            "active": True, # Required. This is a boolean value of whether or not the presented token is currently active. The value should be “true” if the token has been issued by this authorization server, has not been revoked by the user, and has not expired.
            "scope": scope, # A JSON string containing a space-separated list of scopes associated with this token.
            "client_id": user, # The client identifier for the OAuth 2.0 client that the token was issued to.
            "username": user, # A human-readable identifier for the user who authorized this token.
            "exp": unix_expires, # The unix timestamp (integer timestamp, number of seconds since January 1, 1970 UTC) indicating when this token will expire.
        }

        return Response(content)


