from pprint import pprint

import requests
import json
from django.shortcuts import render, redirect

from .forms import UserCreationForm, CreatePartyForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponse
from django.core.signing import BadSignature
from django.http import Http404
from django.core import mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import *
import django_tables2 as tables
from django.contrib.auth.decorators import login_required
from django_tables2.utils import A

class ParticipateTable(tables.Table):
    name = tables.Column(accessor='party.name', verbose_name="Nom de la soirée",)
    resume = tables.Column(accessor='party.resume', verbose_name="Description",)
    datehour = tables.Column(accessor='party.datehour', verbose_name="Date/Heure",)
    place = tables.Column(accessor='party.place', verbose_name="Lieu",)
    organisate = tables.Column(accessor='party.organisate', verbose_name="Organisateur",)
    price = tables.Column(accessor='party.price', verbose_name="Prix",)
    paypal = tables.Column(accessor='party.paypal', verbose_name="Lien Paypal",)
    etat = tables.BooleanColumn(accessor='etat', verbose_name="Participation")
    changer = tables.LinkColumn("ChangeParticipate", text="Modifier", args=[A("pk")], verbose_name="Changer la participation")

    class Meta:
        model = participate
        fields = ('name', 'resume', 'place', 'datehour', 'price', 'paypal', 'organisate', 'etat')
        attrs = {"class": "table table-dark table-striped"}

class PartyTable(tables.Table):
    Name = tables.Column(verbose_name="Nom de la soirée", accessor='name')
    Detail = tables.LinkColumn("party_detail", args=[A("pk")], verbose_name="Détail", text="Détail")
    class Meta:
        model = party
        attrs = {"class": "table table-dark table-striped"}

@login_required
def ChangeParticipate(request, id):
    queryset = participate.objects.filter(pk=id)
    print(queryset[0].utilisateur)
    if queryset[0].utilisateur == request.user:
        queryset.update(etat=(not queryset[0].etat))
    return Home(request)

def party_detail(request, id):
    p = party.objects.get(pk=id)
    return redirect(p.get_absolute_url())

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def Home(request):
    if(request.user):
        queryset = participate.objects.filter(utilisateur=request.user)

        queryset2 = party.objects.filter(organisate=request.user)

        table = ParticipateTable(queryset)

        table2 = PartyTable(queryset2)
        table.exclude = ('id', 'created', 'last_updated',)
        table2.exclude = ('id', 'created', 'last_updated', 'name', 'organisate', 'paypal', 'resume', 'place', 'datehour', 'price')

        return render(request, "home.html", {'table': table, 'table2': table2})
    else:
        return render(request, "home.html")



@login_required
def JoinParty(request):
    if request.method == "POST":
        print(request.POST["id_party"])
        return redirect(request.POST["id_party"]+"/join")
    else:
        return render(request, 'party/join.html')


@login_required
def JoinPartyId(request):
    output = "test"
    return HttpResponse(output)



@login_required
def party_status(request, signed_pk):
    try:
        pk = party.signer.unsign(signed_pk)
        theparty = party.objects.get(id=pk)
        if(request.user == theparty.organisate):
            participants = participate.objects.filter(party=pk, etat=True)
            cocktails = theparty.drink.all()
            tab_cocktails = []
            for cocktail in cocktails:
                url = "https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i="+str(cocktail.id_api)
                r = requests.get(url)
                r_status = r.status_code
                # If it is a success
                if r_status == 200:
                    print(r.text)
                    # convert the json result to python object
                    data = json.loads(r.text)
                    # Loop through the credentials and save them
                    # But it is good to avoid that each user request create new
                    # credentials on top of the existing one
                    # ( you can retrieve and delete the old one and save the news credentials )

                    c=data["drinks"]
                    listIngredients=[c[0]["strIngredient1"],c[0]["strIngredient2"],c[0]["strIngredient3"],c[0]["strIngredient4"],c[0]["strIngredient5"],c[0]["strIngredient6"],c[0]["strIngredient7"],c[0]["strIngredient8"],c[0]["strIngredient9"],c[0]["strIngredient10"],c[0]["strIngredient11"], c[0]["strIngredient12"],c[0]["strIngredient13"],c[0]["strIngredient14"],c[0]["strIngredient15"]]
                    
                    listCocktails = {"idDrink" : c[0]["idDrink"], "strDrink" : c[0]["strDrink"], "listIngredients" : listIngredients}
                    tab_cocktails.append(listCocktails)
            retour = render(request, "party/page.html", {'party': theparty, 'participate' : participants, 'cocktails' : tab_cocktails})
        else:
            retour = redirect("/")
    except (BadSignature, party.DoesNotExist):
        raise Http404('No party matches the given query.')
    return retour


@login_required
def party_join(request, signed_pk):
    try:
        pk_ici = party.signer.unsign(signed_pk)
        party_id = party.objects.get(id=pk_ici)
        verif = participate.objects.filter(utilisateur=request.user, party=party_id)
        if(not verif):
            participate_var = participate(utilisateur=request.user, party=party_id, etat=True)
            participate_var.save()
    except (BadSignature, party.DoesNotExist):
        raise Http404('No party matches the given query.')
    return redirect("/")


@login_required
def create_party(request):
    if request.method == "POST":
        form = CreatePartyForm(request.POST).save(commit=False)
        form.organisate = request.user
        form.save()
        try:
            party_id = party.objects.get(id=form.pk)
            participate_var = participate(utilisateur=request.user, party=party_id, etat=True)
            participate_var.save()
        except (BadSignature, party.DoesNotExist):
            raise Http404('No party matches the given query.')
        return redirect(form.get_absolute_url())
    else:
        form = CreatePartyForm()
        return render(request, 'party/create_form.html', {'form': form})

@login_required
def send_mail(request, signed_pk):
    try:
        pk_ici = party.signer.unsign(signed_pk)
        theparty = party.objects.get(id=pk_ici)
        if (theparty.organisate == request.user):
            html_template = 'mail/message.html'
            html_message = render_to_string(html_template, {'party': theparty})
            from_email="no-reply@partycipe.fr"
            to="noreply.partycipe@gmail.com"
            bcc=["arthur.lambotte51@gmail.com", "arthur.lambotte.auditeur@lecnam.net"]
            message = EmailMessage('Rappel de soirée', html_message, from_email, [to], bcc)
            message.content_subtype = 'html'  # this is required because there is no plain text email message

            message.send()

            return redirect("/")
    except (BadSignature, party.DoesNotExist):
        raise Http404('No party matches the given query.')
    return redirect("/")

@login_required
def share(request, signed_pk):
    try:
        pk = party.signer.unsign(signed_pk)
        theparty = party.objects.get(id=pk)
        if (request.user == theparty.organisate):
            url = "{0}://{1}{2}".format(request.scheme, request.get_host(), request.path)[:-6]
            url=url+"/join"
            retour = render(request, "party/share.html", {'url': url})
        else:
            retour = redirect("/")
    except (BadSignature, party.DoesNotExist):
        raise Http404('No party matches the given query.')
    return retour

@login_required
def add_cocktail(request, signed_pk, id):
    try:
        pk = party.signer.unsign(signed_pk)
        theparty = party.objects.get(id=pk)
        thecocktail = cocktail.objects.filter(id_api=id)
        if (request.user == theparty.organisate):
            if(not thecocktail):
                cocktailinstance = cocktail(id_api=id)
                cocktailinstance.save()
                thecocktail=cocktail.objects.filter(id_api=id)
            theparty.drink.add(thecocktail[0])
        retour = redirect("/party/"+signed_pk)
    except (BadSignature, party.DoesNotExist):
        raise Http404('No party matches the given query.')
    return retour

@login_required
def delete_cocktail(request, signed_pk, id):
    try:
        pk = party.signer.unsign(signed_pk)
        theparty = party.objects.get(id=pk)
        thecocktail = cocktail.objects.filter(id_api=id)
        if (request.user == theparty.organisate):
            theparty.drink.remove(thecocktail[0])
        retour = redirect("/party/"+signed_pk)
    except (BadSignature, party.DoesNotExist):
        raise Http404('No party matches the given query.')
    return retour
