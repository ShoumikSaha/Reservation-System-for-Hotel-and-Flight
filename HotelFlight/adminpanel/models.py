from django.db import models


# Create your models here.

def user_directory_path(instance, filename):
    return 'user_{0}/room_{1}/{2}'.format(instance.userid, instance.roomid, filename)


class Photos(models.Model):
    file = models.FileField(upload_to=user_directory_path)
    roomid = models.IntegerField()
    userid = models.IntegerField()
