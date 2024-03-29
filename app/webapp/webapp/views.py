from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import json
from webapp.models import Token, Profile
from webapp.forms import CreateProfileForm

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

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.dateformat import format as dformat


from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from prometheus_client import Counter, start_http_server

login_counter = Counter("login_counter", "This metric counts the total number of logins")



# set all sage specific cookies here with utility function
# since we don't want to affect global settings
def util_set_cookie(response, key, value):
    response.set_cookie(key, value, domain=settings.SAGE_COOKIE_DOMAIN, secure=True, samesite='Strict')
    return response


@receiver(user_logged_in)
def update_user_login(sender, **kwargs): # Receiver function
    kwargs.pop('user', None)
    login_counter.inc(1)


def home(request, callback = ''):
    uuid = None
    access_token = None
    refresh_token = None

    if request.user.is_authenticated:
        try:
            globus_user = request.user.social_auth.get(provider='globus')
        except:
            if settings.DEBUG:
                uuid = request.user.username
                username = request.user.username


                access_token = 'access_token'
                refresh_token = 'refresh_token'
            else:
                raise Exception("no globus")
        else:
            uuid = globus_user.uid
            social = request.user.social_auth
            access_token = social.get(provider='globus').extra_data['access_token']
            refresh_token = social.get(provider='globus').extra_data['refresh_token']


    # get sage ui redirect if provided
    path = request.GET.get('callback')

    response = render(
        request,
        'home.html',
        {
            'path': path,
            'uuid': uuid,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    )

    # get redirect from previous time callback was provided
    portal_redirect = request.COOKIES.get('portal_redirect')

    # if we have callback, go ahead and store it in cookie
    if path and not portal_redirect:
        response.set_cookie('portal_redirect', path)

    if not request.user.is_anonymous:
        sage_username = request.user.profile.sage_username

    # if we have a token, but no username, redirect to "create_profile" viewa
    if access_token and not sage_username:
        return redirect('/create-profile')

    # if we already have a redirect cookie and are logged in,
    # redirect back to original location
    if portal_redirect and access_token:
        response = redirect(portal_redirect)

        token_object = util_create_sage_token(sage_username)
        expires = token_object.expires
        response = util_set_cookie(response, 'sage_username', sage_username)
        response = util_set_cookie(response, 'sage_token', token_object.tokenValue)
        response = util_set_cookie(response, 'sage_token_exp', "{}/{}/{}".format(expires.month,expires.day,expires.year))
        response.delete_cookie('portal_redirect')

        return response


    return response



# todo(nc): mod expiry time for tokens generated via portal
def util_create_sage_token(user):
    alphabet = string.ascii_uppercase + string.digits
    token_value = ''.join(secrets.choice(alphabet) for i in range(20))
    expires = timezone.now() + timedelta(days=90)

    token_object = Token.objects.create(user=user, tokenValue=token_value, expires=expires, scope="default")

    return token_object



def token(request):
    if request.method == 'GET':
        response_data = {}

        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)

        user_uuid = None
        try:
            user_uuid = request.user.social_auth.get(provider='globus').uid
        except:
            # native Django user, this is mostly for testing purposes
            username = request.user.username
            user_uuid = username

        if user_uuid == None:
            return HttpResponse("user_uuid is empty", status=500)

        sage_username = request.user.profile.sage_username

        token_object = util_create_sage_token(sage_username)
        expires = token_object.expires

        response_data['token'] = token_object.tokenValue
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

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        '''
        Example reqs:
            curl -H 'Accept: application/json; indent=4' -u root:root localhost:8000/token_info/
        '''
        # example: curl -H 'Accept: application/json; indent=4' -u root:root localhost:8000/token_info/

        return Response("hello world")


    def post(self, request, format=None):
        '''
        Example reqs:
            curl -X POST -H 'Accept: application/json; indent=4' -d 'token=abc' -u root:root localhost:8000/token_info/
            curl -X POST -H 'Accept: application/json; indent=4' -d 'token=abc' -u sage-api-user:test localhost:8000/token_info/
        '''

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

        scope = tobject.scope
        user = tobject.user

        unix_expires = int(dformat(expires, 'U'))

        content = {
            "active": True, # Required. This is a boolean value of whether or not the presented token is currently active. The value should be “true” if the token has been issued by this authorization server, has not been revoked by the user, and has not expired.
            "scope": scope, # A JSON string containing a space-separated list of scopes associated with this token.
            "client_id": "some-client-id", # The client identifier for the OAuth 2.0 client that the token was issued to.
            "username": user, # A human-readable identifier for the user who authorized this token.
            "exp": unix_expires, # The unix timestamp (integer timestamp, number of seconds since January 1, 1970 UTC) indicating when this token will expire.
        }

        return Response(content)



def create_profile(request):
    if request.method == 'POST':
        form = CreateProfileForm(request.POST , instance=request.user)
        form.actual_user = request.user
        if form.is_valid():
            form.save()

            # if we have a redirect, prepare the redirect
            path = request.COOKIES.get('portal_redirect')
            response = redirect(path) if path else redirect("/")

            # store username cookie
            sage_username = form.cleaned_data['sage_username']
            response = util_set_cookie(response, 'sage_username', sage_username)

            if (path):
                response.delete_cookie('portal_redirect')

            return response
    else:
        form = CreateProfileForm()

    return render(request, 'create_profile.html', {'form': form})




def portal_logout(request, callback = ''):
    # todo(nc): logout of social
    logout(request)
    messages.info(request, 'Logged out successfully!')

    path = request.GET.get('callback')
    response = redirect(path) if path else redirect("/")

    response.delete_cookie('sage_username', domain=settings.SAGE_COOKIE_DOMAIN)
    response.delete_cookie('sage_uuid', domain=settings.SAGE_COOKIE_DOMAIN)
    response.delete_cookie('sage_token', domain=settings.SAGE_COOKIE_DOMAIN)
    response.delete_cookie('sage_token_exp', domain=settings.SAGE_COOKIE_DOMAIN)
    response.delete_cookie('portal_redirect')

    return response

