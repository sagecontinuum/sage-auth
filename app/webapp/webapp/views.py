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
            return HttpResponse('Unauthorized', status=401)

        
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

        tobject = Token.objects.create(user=user_uuid, tokenValue=tokenValue, expires=expires)
        
        
        response_data['token'] = tobject.tokenValue
        

        response_data['user_uuid'] = user_uuid
        response_data['expires'] = "{}/{}/{}".format(expires.month,expires.day,expires.year)
       
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    pass
