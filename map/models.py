from django.db import models

# Create your models here.
class Photo(models.Model):
    file_name = models.CharField(max_length=50)
    file_path = models.CharField(max_length=200,unique=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    create_date = models.DateTimeField('date created')
    address = models.CharField(max_length=200)
    image_make = models.CharField(max_length=20)
    image_model = models.CharField(max_length=50)

    def __str__(self):
        return 'map %s' % self.file_name

    class Meta:
        app_label = 'map'