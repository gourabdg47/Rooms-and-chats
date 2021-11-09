from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)                  # Room, is the child of a "Topic"

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # participants =   # Store all the users
    updated = models.DateTimeField(auto_now=True)            # takes time stamp everytime it's updated
    created = models.DateTimeField(auto_now_add=True)        # takes timestanm onetime it's initiated

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name                                     # sending the name of the room when this class is called from the admin pannel


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 1 to many user model (default django usermodel)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # When a room is deleted, .CASCADE means it will delete all the messages as well from the database
    body = models.TextField()                                # message body from the users
    updated = models.DateTimeField(auto_now=True)            # takes time stamp everytime it's updated
    created = models.DateTimeField(auto_now_add=True)        # takes timestanm onetime it's initiated

    def __str__(self):
        return self.body[0:50]                               # sending the body of the message when this class is called from the admin pannel