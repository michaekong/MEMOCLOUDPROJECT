from django.db import models
from django.contrib.auth.hashers import make_password

from django.db import models
from django.contrib.auth.hashers import make_password

class UserProfile(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('A', 'Autre'),
    ]

    TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('admin', 'Administrateur'),
        ('superadmin', 'superAdministrateur'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES ,default='standard')
    realisation_linkedin = models.URLField(max_length=200, blank=True, null=True)
    photo_profil = models.ImageField(upload_to='photos_profil/', blank=True, null=True)
    password = models.CharField(max_length=128)
   
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Domaine(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom
from django.db import models

class UnverifiedUserProfile(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
   
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    type = models.CharField(max_length=50,default='standard')
    realisation_linkedin = models.URLField(null=True, blank=True)
    photo_profil = models.ImageField(upload_to='profiles/', null=True, blank=True)
    password = models.CharField(max_length=255)  # Mot de passe haché
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Memoire(models.Model):
    titre = models.CharField(max_length=200)
    domaines = models.ManyToManyField(Domaine, related_name='memoires')
    annee_publication = models.PositiveIntegerField()
    images = models.ImageField(upload_to='memoires/images/', blank=True, null=True)
    auteur = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='memoires')
    resume = models.TextField()
    fichier_memoire = models.FileField(upload_to='memoires/pdf/', blank=False, null=False)
    def note_moyenne(self):
        notes = self.notations.values_list('note', flat=True)
        return round(sum(notes) / len(notes), 2) if notes else 0
    
    def __str__(self):
        return self.titre

class NotationCommentaire(models.Model):
    memoire = models.ForeignKey(Memoire, on_delete=models.CASCADE, related_name='notations')
    utilisateur = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notations')
    commentaire = models.TextField(blank=True, null=True)
    note = models.PositiveIntegerField(default=1)  # Note entre 1 et 5
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note: {self.note} - {self.utilisateur.prenom} sur {self.memoire.titre}"

    class Meta:
        unique_together = ('memoire', 'utilisateur')  # Un utilisateur peut noter/commenter un mémoire une seule fois


class Visiteur(models.Model):
    emailv = models.EmailField()    
    datev = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.emailv

class Encadrement(models.Model):
    memoire = models.ForeignKey(Memoire, on_delete=models.CASCADE, related_name='encadrements')
    encadrant = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='encadrements')
   
    def __str__(self):
        return self.memoire.titre

class Telechargement(models.Model):
    memoire = models.ForeignKey(Memoire, on_delete=models.CASCADE, related_name='telechargements')
    emailt = models.EmailField()
    datet = models.DateTimeField(auto_now_add=True)
