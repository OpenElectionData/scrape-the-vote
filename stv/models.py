from django.db import models

class Election(models.Model) :
    election_name = models.CharField(max_length=1000)

class ElectionReport(models.Model) :
    image = models.FileField()
    hash = models.CharField(max_length=1000, unique=True)
    url = models.URLField()
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    election = models.ForeignKey(Election)
    
