from django.test import TestCase
from django.contrib.auth.models import User
from .views import util_create_sage_token
import json



class UserProfileTests(TestCase):

    def testUserProfileNoAuth(self):
        r = self.client.get('/user_profile/test')
        self.assertEqual(r.status_code, 403)

    def testUserProfileBadAuth(self):
        r = self.client.get('/user_profile/test')
        self.assertEqual(r.status_code, 403)

        r = self.client.get('/user_profile/test', HTTP_AUTHORIZATION='Notvalid')
        self.assertEqual(r.status_code, 403)

        r = self.client.get('/user_profile/test', HTTP_AUTHORIZATION='Sage some_foo')
        self.assertEqual(r.status_code, 403)

        data = {'bio': 'a new bio'}
        r = self.client.put('/user_profile/test', data, HTTP_AUTHORIZATION='Sage some_foo', content_type='application/json')
        self.assertEqual(r.status_code, 403)

    def testUserProfileBadBearer(self):
        r = self.client.get('/user_profile/test', HTTP_AUTHORIZATION='Foo some_foo')
        self.assertEqual(r.status_code, 403)

    def testUserProfileView(self):
        token = self.setUpUserAndToken('test')
        authorization = f'Sage {token}'

        r = self.client.get('/user_profile/test', HTTP_AUTHORIZATION=authorization)
        self.assertEqual(r.status_code, 200)

        u = json.loads(r.content)
        self.assertEqual(u['bio'], 'a bio')
        self.assertEqual(u['department'], 'a department')
        self.assertEqual(u['organization'], 'an org')

    def testUserProfileUpdate(self):
        token = self.setUpUserAndToken('test')
        authorization = f'Sage {token}'

        # do an update
        data = {'bio': 'a new bio', 'department': 'new department'}
        r = self.client.put('/user_profile/test', data, HTTP_AUTHORIZATION=authorization, content_type='application/json')
        self.assertEqual(r.status_code, 200)

        u = json.loads(r.content)
        self.assertEqual(u['bio'], 'a new bio')
        self.assertEqual(u['department'], 'new department')
        self.assertEqual(u['organization'], 'an org')

        # check db
        r = self.client.get('/user_profile/test', HTTP_AUTHORIZATION=authorization)
        self.assertEqual(r.status_code, 200)

        u = json.loads(r.content)
        self.assertEqual(u['bio'], 'a new bio')
        self.assertEqual(u['department'], 'new department')
        self.assertEqual(u['organization'], 'an org')

    def setUpUserAndToken(self, username):
        '''create a user with an empty profile and random token'''
        user = User.objects.create_user(username, '', 'test')
        user.profile.sage_username = username
        user.profile.bio = 'a bio'
        user.profile.department = 'a department'
        user.profile.organization = 'an org'
        user.save()
        token = util_create_sage_token(username)
        return token.tokenValue