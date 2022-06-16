from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.signing import Signer

class cocktail(models.Model):
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    id_api = models.PositiveIntegerField()

    def __str__(self):
        return str(self.id_api)

class party(models.Model):
    drink = models.ManyToManyField(cocktail)
    organisate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    paypal = models.URLField()
    name = models.CharField(max_length=50)
    resume = models.CharField(max_length=500)
    place = models.CharField(max_length=150)
    datehour = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    price = models.FloatField()
    signer = Signer(sep='/', salt='party.party')

    def get_absolute_url(self):
        signed_pk = self.signer.sign(self.pk)
        return reverse('party-status', kwargs={'signed_pk': signed_pk})

    def __str__(self):
        return self.name

class participate(models.Model):
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    party = models.ForeignKey(party, on_delete=models.CASCADE)
    etat = models.BooleanField()

    def __str__(self):
        return str(self.etat)