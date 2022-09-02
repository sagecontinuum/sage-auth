from webapp.models import Token, Profile

from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import authentication



def get_token_user(token):
    try:
        t_object = Token.objects.get(tokenValue=token)
    except Token.DoesNotExist:
        return None

    if t_object == None:
        return None

    expires = t_object.expires

    if expires == None or timezone.now() > expires:
        return None

    return t_object.user



class Authentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        sage_username = get_token_user(token.split(' ')[1])

        if not sage_username:
            raise exceptions.AuthenticationFailed

        try:
            user_profile = Profile.objects.get(sage_username=sage_username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user profile')

        # use sage user_profile instead of django auth User
        request.sage_username = user_profile.sage_username

        return (user_profile, None)



immutable_fields = ['id', 'user_id', 'sage_username']

class UserProfile(APIView):
    authentication_classes = [Authentication]

    def get(self, request, **kwargs):
        '''
        Example request:
            curl -H 'Authorization: Sage <token>' localhost:8000/user_profile/<username>
        '''

        user_param = kwargs.get('username')
        username = request.sage_username

        if user_param != username:
            raise exceptions.AuthenticationFailed


        if username:
            data = Profile.objects.filter(sage_username=username).values()
        else:
            data = Profile.objects.all().values() # todo(nc): remove full listing, and allow limited queries

        return Response({'data': data})


    def post(self, request, **kwargs):
        '''
        Example request:
            curl -X POST -H "Content-Type: application/json" -H 'Authorization: Sage <token>'
            localhost:8000/user_profile/<username> -d '{"bio": "some bio"}'
        '''
        user_param = kwargs.get('username')
        username = request.sage_username

        if user_param != username:
            raise exceptions.AuthenticationFailed


        record = Profile.objects.filter(sage_username=username)

        for field in request.data.keys():
            if field in immutable_fields:
                continue

            record.update(**{field: request.data[field]})

        return Response(
            Profile.objects.filter(sage_username=username).values()
        )


