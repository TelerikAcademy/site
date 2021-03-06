import string

from django.contrib.auth.models import User

from dmoj import settings

import json

import requests

from judge.models import Profile, Language


class RemoteUserBackend(object):
    def get_login_url(self, api_key, username, password):
        return 'https://telerikacademy.com/Api/Users/CheckUserLogin?apiKey=%s&usernameoremail=%s&password=%s' % (
            api_key, username, password)

    def authenticate(self, username=None, password=None):
        # Telerik Academy Authentication

        r = requests.post(self.get_login_url(settings.API_KEY, username, password))
        result = json.loads(r.content)

        if result['IsValid']:
            real_username = result['UserName']

            try:
                user = User.objects.get(username=real_username)
            except User.DoesNotExist:
                user = User(username=real_username)

                user.save()

            profile, _ = Profile.objects.get_or_create(user=user, defaults={
                'language': Language.get_python2(),
                'timezone': 'Europe/Sofia',
            })

            profile.name = real_username
            small_avatar_url = result['SmallAvatarUrl']
            normal_avatar_url = string.replace(small_avatar_url, '32x32', '180x180')
            print(normal_avatar_url)
            profile.avatar = normal_avatar_url

            profile.save()

            if result['IsAdmin']:
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False
            user.save()

            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
