"""
URL configuration for MEMOIRE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from memoire.views import *
from django.conf import settings 
from django.conf.urls.static import static


urlpatterns = [
    path('',common, name='home'),
    path('admin/', admin.site.urls),
    path('home',  home,name="home"),
    path('register', register_user,name="register"),
    path('login',  login,name="login"),
    path('common',  common,name="common"),
    path('profil',  profil,name="profil"),
    path('eprofil',  profil,name="eprofil"),
    path('admins',  admins,name="admins"),
    path('admins/', admins, name='admins'),
    path('delete_memoire/', delete_memoire, name='delete_memoire'),
    path('delete_user/', delete_user, name='delete_user'),
    path('delete_encadrement/', delete_encadrement, name='delete_encadrement'),
    path('add_user/',add_user, name='add_user'),
    path('add_memoire/', add_memoire, name='add_memoire'),
    path('add_encadrement/', add_encadrement, name='add_encadrement'),
    path('edit_user/', edit_user, name='edit_user'),
     path('edit_domaine/', edit_domaine, name='edit_domaine'),
     path('delete_domaine/', delete_domaine, name='delete_domaine'),
     path('add_domaine/', add_domaine, name='add_domaine'),
    path('edit_memoire/', edit_memoire, name='edit_memoire'),
    path('edit_encadrement/', edit_encadrement, name='edit_encadrement'),
    path('telecharger_pdf', telecharger_pdf,name="telecharger_pdf"),
    
    path('send_welcome_email/', send_welcome_email,name="send_welcome_email"),
    
 
    path('edit_profile',  edit_profile,name="edit_profile"),
    path('verification_page', verification_page, name='verification'),
     path('connection', verification_Email, name='verification'),
    path('liste_memoires/', liste_memoires, name='liste_memoires'),
    path('logout/',logout, name='logout'),
   
     path('send_welcome_email', send_welcome_email,name="send_welcome_email"),
    


    
    
]

if settings.DEBUG:
    urlpatterns+= static (settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
