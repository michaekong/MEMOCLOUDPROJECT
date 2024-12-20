from django.contrib import admin
from .models import *
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'type', 'sexe', 'birthday')
    list_filter = ('type', 'sexe')
    search_fields = ('nom', 'prenom', 'email')


@admin.register(Domaine)
class DomaineAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Memoire)
class MemoireAdmin(admin.ModelAdmin):
    list_display = ('titre', 'annee_publication', 'auteur', 'note_moyenne_display')
    list_filter = ('annee_publication', 'domaines')
    search_fields = ('titre', 'resume', 'auteur__nom', 'auteur__prenom')
    autocomplete_fields = ('auteur', 'domaines')

    def note_moyenne_display(self, obj):
        return obj.note_moyenne()
    note_moyenne_display.short_description = "Note Moyenne"


@admin.register(NotationCommentaire)
class NotationCommentaireAdmin(admin.ModelAdmin):
    list_display = ('memoire', 'utilisateur', 'note', 'date_creation', 'commentaire_preview')
    list_filter = ('note', 'date_creation')
    search_fields = ('memoire__titre', 'utilisateur__nom', 'utilisateur__prenom', 'commentaire')

    def commentaire_preview(self, obj):
        return obj.commentaire[:50] if obj.commentaire else "Pas de commentaire"
    commentaire_preview.short_description = "Commentaire"


@admin.register(Visiteur)
class VisiteurAdmin(admin.ModelAdmin):
    list_display = ('emailv', 'datev')
    search_fields = ('emailv',)


@admin.register(Encadrement)
class EncadrementAdmin(admin.ModelAdmin):
    list_display = ('memoire', 'encadrant')
    search_fields = ('memoire__titre', 'encadrant__nom', 'encadrant__prenom')


@admin.register(Telechargement)
class TelechargementAdmin(admin.ModelAdmin):
    list_display = ('memoire', 'emailt', 'datet')
    list_filter = ('datet',)
    search_fields = ('memoire__titre', 'emailt')
@admin.register(UnverifiedUserProfile)
class UnverifiedUserProfileAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'created_at', 'verification_code')
    search_fields = ('nom', 'prenom', 'email')
    list_filter = ('created_at',)