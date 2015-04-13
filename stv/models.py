from django.db import models

class Image(models.Model) :
    image = models.FileField()
    image_url = models.URLField()
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    
