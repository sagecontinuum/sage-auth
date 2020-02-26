from django.shortcuts import render
from django.http import HttpResponse
import json

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
        if request.user.is_authenticated:
            response_data['token'] = 'I_AM_A_TOKEN'
        else:
            response_data['token'] = 'I_AM_A_TOKEN (but you are not logged in)'

        response_data['message'] = 'some message'
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    pass
