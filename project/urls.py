"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from partycipe.views import *

from welcome.views import index, health

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', Home),
    #path('', index, name='home'),
    path('health/', health),
    path('admin/', admin.site.urls),
    
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),

    

    path('party/join', JoinParty),
    path('party/partipate', JoinParty),
    path('party/create', create_party),
    path('party/<int:id>', party_detail, name='party_detail'),



    path('participate/change/<int:id>', ChangeParticipate, name="ChangeParticipate"),

    re_path(r'party\/(?P<signed_pk>(?:[0-9]+\/[A-Za-z0-9_=-]+))$', party_status, name='party-status'),
    re_path(r'party\/(?P<signed_pk>(?:[0-9]+\/[A-Za-z0-9_=-]+))\/join$', party_join, name='party-join'),

    re_path(r'party\/(?P<signed_pk>(?:[0-9]+\/[A-Za-z0-9_=-]+))\/mail$', send_mail, name='send_mail'),
    re_path(r'party\/(?P<signed_pk>(?:[0-9]+\/[A-Za-z0-9_=-]+))\/share$', share, name='share'),

    re_path(r'party\/(?P<signed_pk>(?:[0-9]+\/[A-Za-z0-9_=-]+))\/add_cocktail\/(?P<id>(?:[0-9]+))', add_cocktail, name='add_cocktail'),
    re_path(r'party\/(?P<signed_pk>(?:[0-9]+\/[A-Za-z0-9_=-]+))\/delete_cocktail\/(?P<id>(?:[0-9]+))', delete_cocktail, name='delete_cocktail'),

    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='registration/change_password.html',success_url = '/'),name='change_password'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
