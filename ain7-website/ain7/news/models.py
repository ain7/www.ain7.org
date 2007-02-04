from django.db import models

class Actualite(models.Model):

    titre = models.CharField(maxlength=100)
    description = models.TextField()
    image = models.ImageField(upload_to='data',null=True,blank=True)

    date_creation = models.DateTimeField()
    date_modification = models.DateTimeField()


    class Admin:
        list_display = ('titre','description')


