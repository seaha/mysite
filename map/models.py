from django.db import models

# Create your models here.
class Photo(models.Model):
    file_name = models.CharField(max_length=50)
    file_path = models.CharField(max_length=200)
    longitude = models.FloatField()
    latitude = models.FloatField()
    create_date = models.DateTimeField('date created')
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.file_name