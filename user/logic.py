import os

from django.conf import settings

from common import keys



def handle_uploaded_file(uid, avatar):
    filename = keys.AVATAR_KEY % uid
    filepath = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, filename)
    with open(filepath, mode='wb+') as fp:
        for chunk in avatar.chunks():
            fp.write(chunk)
