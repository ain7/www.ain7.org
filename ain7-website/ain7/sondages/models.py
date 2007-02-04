from django.db import models

class Sondage(models.Model):
    question = models.CharField(maxlength=200)
    pub_date = models.DateTimeField('date publication')
#    en_ligne = models.BooleanField()

    class Admin:
	list_display = ('question', 'pub_date')

class Choix(models.Model):
    sondage = models.ForeignKey(Sondage, edit_inline=models.STACKED, num_in_admin=3)
    choice = models.CharField(maxlength=200, core=True)
    votes = models.IntegerField()

