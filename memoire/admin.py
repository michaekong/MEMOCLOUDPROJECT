from django.contrib import admin
from .models import *


class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('prenom', 'nom', 'email', 'type')

    search_fields = ('prenom', 'nom', 'email')

    list_filter = ('type',)


class MemoireAdmin(admin.ModelAdmin):

    list_display = ('titre', 'domaine', 'annee_publication', 'auteur')

    search_fields = ('titre', 'domaine', 'auteur__prenom', 'auteur__nom')

    list_filter = ('domaine', 'annee_publication', 'auteur')


class EncadrementAdmin(admin.ModelAdmin):

    list_display = ('memoire', 'encadrant')

    search_fields = ('memoire__titre', 'encadrant__prenom', 'encadrant__nom')

    list_filter = ('memoire', 'encadrant')


class visiteurAdmin(admin.ModelAdmin):

    list_display = ('emailv', 'datev')

    search_fields = ('emailv', 'datev')

    list_filter = ('emailv', 'datev')
class telechargementAdmin(admin.ModelAdmin):

    list_display = ('emailt', 'memoire')

    search_fields = ('memoire', 'emailt')

    list_filter = ('memoire', 'emailt')


# Enregistrement des modèles dans l'admin

admin.site.register(telechargement, telechargementAdmin)    


# Enregistrement des modèles dans l'admin

admin.site.register(visiteur, visiteurAdmin)
# Enregistrement des modèles dans l'admin

admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Memoire, MemoireAdmin)

admin.site.register(Encadrement, EncadrementAdmin)

# Register your models here.
