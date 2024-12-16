from django.db import models
from django import forms


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
    birthday = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    realisation_linkedin = models.URLField(max_length=200, blank=True, null=True)
    photo_profil = models.ImageField(upload_to='photos_profil/', blank=True, null=True)
    password = models.CharField(max_length=128 ,default="aaaaa")
   

    def save(self, *args, **kwargs):
        # Hash the password before saving if it's not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    

class Memoire(models.Model):
    titre = models.CharField(max_length=200)
    domaine = models.CharField(max_length=100)
    annee_publication = models.PositiveIntegerField()
    images = models.ImageField(upload_to='memoires/images/', blank=True, null=True)
    auteur = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='memoires')
    resume = models.TextField()
    fichier_memoire = models.FileField(upload_to='memoires/pdf/',blank=False,null=False)
    

    def __str__(self):
        return self.titre
class visiteur(models.Model):
    emailv = models.EmailField()    
    datev=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.emailv

class Encadrement(models.Model):
    memoire = models.ForeignKey(Memoire, on_delete=models.CASCADE, related_name='encadrements')
    encadrant = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='encadrements')
   
    

    def __str__(self):
        return self.memoire.titre
class telechargement(models.Model):
    memoire=models.ForeignKey(Memoire, on_delete=models.CASCADE, related_name='telechargements')
    emailt= models.EmailField()
    datet=models.DateTimeField(auto_now_add=True )