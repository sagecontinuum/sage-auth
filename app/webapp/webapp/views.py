from django.shortcuts import render
from django.http import HttpResponse
import json
from webapp.models import Token
import secrets

from django.utils import timezone
import pytz
from datetime import datetime, timedelta
import string 



def home(request):
    uuid = None
    access_token = None
    refresh_token = None
    if request.user.is_authenticated:
        uuid = request.user.social_auth.get(provider='globus').uid
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

        
        
        alphabet = string.ascii_uppercase + string.digits
        tokenValue = ''.join(secrets.choice(alphabet) for i in range(20))

        expires = timezone.now() + timedelta(days=90)  

        if request.user.is_authenticated:
            user_uuid = request.user.social_auth.get(provider='globus').uid
        else:
            user_uuid="anonymous"

        tobject = Token.objects.create(user=user_uuid, tokenValue=tokenValue, expires=expires)
        
        if request.user.is_authenticated:
            response_data['token'] = tobject.tokenValue
        else:
            response_data['token'] = tobject.tokenValue + " you are not logged in !"

        response_data['user_uuid'] = user_uuid
        response_data['expires'] = "{}/{}/{}".format(expires.month,expires.day,expires.year)
       
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    pass
