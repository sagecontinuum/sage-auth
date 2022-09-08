from webapp.models import Token, Profile

from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.serializers import ModelSerializer
from rest_framework.authentication import BaseAuthentication
from rest_framework.generics import RetrieveUpdateAPIView



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


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')

        if not auth:
            raise exceptions.AuthenticationFailed('No Authorization header provided')

        try:
            [bearer, token] = auth.split(' ')
        except:
           raise exceptions.AuthenticationFailed('Invalid format')

        if not token:
            raise exceptions.AuthenticationFailed('No token provided')

        if bearer.lower() != 'sage':
            raise exceptions.AuthenticationFailed(f'Invalid bearer: {bearer}')

        sage_username = get_token_user(token)

        if not sage_username:
            raise exceptions.AuthenticationFailed

        try:
            user_profile = Profile.objects.get(sage_username=sage_username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user profile')

        # use sage user_profile instead of django auth User
        request.sage_username = user_profile.sage_username

        return (user_profile, None)


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        lookup_field = 'sage_username'
        fields = '__all__'
        read_only_fields = ['user', 'sage_username']


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sage_username == request.sage_username


'''
Example requests:
    curl -H 'Authorization: Sage <token>' localhost:8000/user_profile/<username>
    curl -X PUT -H "Content-Type: application/json" -H 'Authorization: Sage <token>' localhost:8000/user_profile/<username> -d '{"bio": "some bio"}'
'''
class UserProfile(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "sage_username"
    authentication_classes = [Authentication]
    permission_classes = [IsOwner]


