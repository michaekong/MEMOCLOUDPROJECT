from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from django.core.mail import send_mail
import random
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect

from django.db.models import Q
from .models import *

from django.db.models import Prefetch, Q
from django.db.models import Count
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from .models import UserProfile, Memoire, Telechargement as telechargement, Encadrement,   Visiteur as visiteur



from django.contrib.auth.hashers import make_password

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect


def edit_profile(request):
    # Récupérer l'utilisateur connecté
   
    try:
        idp=request.session['user_id']
        user = UserProfile.objects.get(id=idp)
    
        user_profile = user
    except UserProfile.DoesNotExist:
        messages.error(request, "Profil introuvable.")
        return redirect('login')

    if request.method == 'POST':
        # Récupération des champs du formulaire
        nom = request.POST.get('nom', user_profile.nom)
        prenom = request.POST.get('prenom', user_profile.prenom)
        birthday = request.POST.get('birthday', user_profile.birthday)
        sexe = request.POST.get('sexe', user_profile.sexe)
        user_type = request.POST.get('type', user_profile.type)
        realisation_linkedin = request.POST.get('realisation_linkedin', user_profile.realisation_linkedin)
        photo_profil = request.FILES.get('photo_profil')

        # Mise à jour des informations utilisateur
        user_profile.nom = nom
        user_profile.prenom = prenom
        user_profile.birthday = birthday
        user_profile.sexe = sexe
        user_profile.type = user_type
        user_profile.realisation_linkedin = realisation_linkedin
        if photo_profil:
            user_profile.photo_profil = photo_profil
        user_profile.save()

        # Gestion du changement de mot de passe
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password or confirm_password:
            if new_password == confirm_password:
                user.password=make_password(new_password ) # Utilise set_password pour gérer le hash
                user.save()
                messages.success(request, "Mot de passe modifié avec succès.")
                return redirect('login')  # Rediriger pour que l'utilisateur se reconnecte
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return render(request, 'edit_profile.html', {'user': user_profile})

        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('logout')

    return render(request, 'edit_profile.html', {'user': user_profile})


def register_user(request, *args, **kwargs):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        birthday = request.POST.get('birthday')
        sexe = request.POST.get('sexe')
        email = request.POST.get('email')
        user_type = request.POST.get('type')
        realisation_linkedin = request.POST.get('realisation_linkedin', None)
        photo_profil = request.FILES.get('photo_profil', None)
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation des mots de passe
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('/register')

        # Vérifier si un utilisateur avec le même email existe déjà
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà.")
            return redirect('/register')

        try:
            

            # Hachage du mot de passe
            hashed_password = make_password(password)

            # Création de l'utilisateur
            user = UserProfile.objects.create(
                nom=nom,
                prenom=prenom,
                birthday=birthday,
                sexe=sexe,
                email=email,
                type=user_type,
                realisation_linkedin=realisation_linkedin,
                photo_profil=photo_profil,
                password=hashed_password,  # Enregistrer le mot de passe haché
            )
            user.save()
            subjet='verification code '
            email=request.POST.get("email")
            # Génération du code de vérification à 6 chiffres
            verification_code = random.randint(100000, 999999)
            request.session['verification_code'] = verification_code
            request.session['user_email'] = email  
            
            user = UserProfile.objects.get(email=email)
            template='template.html'
            context={
                'date':datetime.today().date,
                'email':email,
                'user':user,
                'verification_code':verification_code,
                
                
                    }
            receivers=[email]
            send_advanced_email(recipient =receivers, subject=subjet, template=template, context=context)


# Envoi de l'
          # Enregistrez le code de vérification en session
                # Adresse e-mail sous forme de chaîne
            return render(request, "verified.html")  # Redirigez vers une page de vérification
            

        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")
            return redirect('/register')

    return render(request, "register.html")



# Create your views here.
def home(request,*args, **kwargs):
    return HttpResponse("<h2 >Options de la Carte</h2>")

from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def profil(request):
    """
    Vue pour afficher les informations du profil de l'utilisateur connecté.
    """
    try:
        
        idp=request.session['user_id']
        user = UserProfile.objects.get(id=idp)
    except:
        return redirect("logout")    
    return render(request, 'profil.html', {'user': user})


def login(request, *args, **kwargs):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Recherche de l'utilisateur par email
            user = UserProfile.objects.get(email=email)

            # Vérification du mot de passe
            if check_password(password, user.password):
                # Simule une connexion (vous pouvez utiliser des sessions)
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                request.session['emailv'] = user.email
                messages.success(request, "Connexion réussie. Bienvenue !")
                
                if(user.type == "admin" or  user.type=="superadmin"):
                    return redirect('/admins') 
                else:
                    return redirect('liste_memoires')
                    
                    # Redirige vers la page d'accueil
            else:
                messages.error(request, "Mot de passe incorrect.")
        except UserProfile.DoesNotExist:
            messages.error(request, "Utilisateur introuvable avec cet email.")

        return redirect('/login')  # Recharge la page de connexion

    return render(request, "login.html")

def logout(request):
    # Supprimer les informations de session
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    
    # Message de succès
    messages.success(request, "Déconnexion réussie. À bientôt !")
    
    # Rediriger vers la page de connexion
    return redirect('/login')




from django.shortcuts import render
from django.db.models import Q, Prefetch
from django.db.models import Q, Count, Avg, Prefetch
from django.shortcuts import render
from .models import Memoire, Domaine, Encadrement, UserProfile

from django.db.models import Count, Avg, Prefetch, Q

def liste_memoires(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)
    
    # Récupérer tous les mémoires avec leurs relations
    memoires = Memoire.objects.prefetch_related(
        Prefetch(
            'encadrements',
            queryset=Encadrement.objects.select_related('encadrant'),
            to_attr='encadreur_list'
        ),
        'domaines'  # Préfetch des domaines
    ).annotate(
        nbr_telechargements=Count('telechargements'),  # Nombre de téléchargements
        note_moyenne=Avg('notations__note')  # Moyenne des notes
    )

    # Filtres de recherche
    query = request.GET.get('q')
    if query:
        memoires = memoires.filter(
            Q(titre__icontains=query) |
            Q(domaines__nom__icontains=query) |
            Q(auteur__prenom__icontains=query) |
            Q(auteur__nom__icontains=query) |
            Q(resume__icontains=query)
        ).distinct()

    # Filtres additionnels
    domaine_id = request.GET.get('domaine')
    annee = request.GET.get('annee')
    encadreur_id = request.GET.get('encadreur')
    auteur_id = request.GET.get('auteur')

    if domaine_id:
        memoires = memoires.filter(domaines__id=domaine_id)

    if annee:
        memoires = memoires.filter(annee_publication=annee)

    if encadreur_id:
        memoires = memoires.filter(encadrements__encadrant__id=encadreur_id)

    if auteur_id:
        memoires = memoires.filter(auteur__id=auteur_id)

    # Données pour les filtres
    domaines_uniques = Domaine.objects.all()
    annees_uniques = Memoire.objects.values_list('annee_publication', flat=True).distinct()
    encadreurs_uniques = UserProfile.objects.filter(encadrements__isnull=False).distinct()
    auteurs_uniques = UserProfile.objects.filter(memoires__isnull=False).distinct()
    

    # Contexte pour le template
    context = {
        'memoires': memoires,
        'domaines': domaines_uniques,
        'annees': annees_uniques,
        'encadreurs': encadreurs_uniques,
        'auteurs': auteurs_uniques,
        'query_params': request.GET,
        'user':user,
        'champs': ['domaine', 'annee', 'encadreur', 'auteur'],  # Utilisé pour simplifier les templates
    }

    return render(request, 'memoire.html', context)



def common(request,*args, **kwargs):
   

    return render(request, "index.html")
    
    
   
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import *
from django.db.models.functions import ExtractMonth
# Vue principale qui charge les données pour le tableau de bord
def admins(request, *args, **kwargs):
    # Fetching data for memoires, users, and encadrements
    memoires = Memoire.objects.prefetch_related(
        Prefetch(
            'encadrements',
            queryset=Encadrement.objects.select_related('encadrant'),
            to_attr='encadreur_list'
        ),
        'domaines'  # Préfetch des domaines
    ).annotate(
        nbr_telechargements=Count('telechargements'),  # Nombre de téléchargements
        note_moyenne=Avg('notations__note')  # Moyenne des notes
    )  # Comptage des téléchargements pour chaque mémoire
    utilisateurs = UserProfile.objects.all()
    encadrements = Encadrement.objects.all()
    comments=NotationCommentaire.objects.all()
    total_comments=NotationCommentaire.objects.count()
    total_dom = Domaine.objects.count()
    dom = Domaine.objects.all()
    vis = visiteur.objects.all()
    tel = telechargement.objects.all()
    # Récupération des données
    total_users = UserProfile.objects.count()
    total_memoires = Memoire.objects.count()
    total_encadrements = Encadrement.objects.count()
    total_telechargements = telechargement.objects.count()
    total_visites=visiteur.objects.count()

    
    
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)
  
    
    # Context for rendering the page
    context = {
        'memoires': memoires,
        'utilisateurs': utilisateurs,
        'encadrements': encadrements,
        'visiteurs': vis,
        'telechargement': tel,
        'user': user,
        'total_users': total_users,
        'total_memoires': total_memoires,
        'total_encadrements': total_encadrements,
        'total_telechargements': total_telechargements,
        'total_visites':total_visites,
        'domaines':dom,
        'comments':comments,
        'total_dom':total_dom,
        'total_comments':total_comments,
        
       
    }
    
    return render(request, "admin.html", context)

# Supprimer un mémoire
def delete_memoire(request):
    if request.method == 'POST':
        memoire_id = request.POST.get('memoire_id')
        try:
            memoire = get_object_or_404(Memoire, id=memoire_id)
            memoire.delete()
            return JsonResponse({'status': 'success', 'message': 'Mémoire supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
def delete_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        try:
            comment = get_object_or_404(NotationCommentaire, id=comment_id)
            comment.delete()
            return JsonResponse({'status': 'success', 'message': 'commentaire supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})        
def delete_domaine(request):
    if request.method == 'POST':
        domaine_id = request.POST.get('domaine_id')
        print(domaine_id)
        try:
            domaine = get_object_or_404(Domaine, id=domaine_id)
            domaine.delete()
            return JsonResponse({'status': 'success', 'message': 'Domaine supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})        

# Supprimer un utilisateur
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = get_object_or_404(UserProfile, id=user_id)
            user.delete()
            messages.success(request, 'Utilisateur supprimé avec succès.')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
        return redirect('admins')



# Supprimer un encadrement
def delete_encadrement(request):
    if request.method == 'POST':
        encadrement_id = request.POST.get('encadrement_id')
        try:
            encadrement = get_object_or_404(Encadrement, id=encadrement_id)
            encadrement.delete()
            return JsonResponse({'status': 'success', 'message': 'Encadrement supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

# Ajouter un utilisateur
def add_user(request):
    if request.method == 'POST':
        try:
            UserProfile.objects.create(
                nom=request.POST.get('nom'),
                prenom=request.POST.get('prenom'),
                birthday=request.POST.get('birthday'),
                sexe=request.POST.get('sexe'),
                email=request.POST.get('email'),
                type=request.POST.get('type'),
                realisation_linkedin=request.POST.get('realisation_linkedin'),
                photo_profil=request.FILES.get('photo_profil'),
                password=make_password(request.POST.get('password'))
            )
            messages.success(request, 'Utilisateur ajouté avec succès.')  # Message de succès
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")  # Message d'erreur
        return redirect('admins')  # Redirection après l'opération

# Ajouter un mémoire
def add_memoire(request):
    if request.method == 'POST':
        
        try:
            auteur_id = request.POST.get('auteur')
            auteur = get_object_or_404(UserProfile, id=auteur_id)
            if 'lien_telecharger' in request.FILES:
                
                fich = request.FILES.get('lien_telecharger')
                print(fich)
            Memoire.objects.create(
                titre=request.POST.get('titre'),
                domaine=request.POST.get('domaine'),
                annee_publication=request.POST.get('annee_publication'),
                images=request.FILES.get('images'),
                auteur=auteur,
                resume=request.POST.get('resume'),
                
                
                fichier_memoire = fich
                
            )
            return redirect("admins")
        except :
            messages.error(request, "erreur d'ajout du lien d'encadrement.")
            return redirect("admins")
def add_domaine(request):
    if request.method == 'POST':
        
        try:
            Domaine.objects.create(
                nom=request.POST.get('nom'),
               
                
            )
            return redirect("admins")
        except :
            messages.error(request, "erreur d'ajout du domaine.")
            return redirect("admins")

# Ajouter un encadrement
def add_encadrement(request):
    if request.method == 'POST':
        try:
            memoire_id = request.POST.get('memoire')
            encadrant_id = request.POST.get('encadrant')
            memoire = get_object_or_404(Memoire, id=memoire_id)
            encadrant = get_object_or_404(UserProfile, id=encadrant_id)
            Encadrement.objects.create(memoire=memoire, encadrant=encadrant)
            messages.success(request, "Encadrement ajouté avec succès.")
            return redirect("admins")
        except :
            messages.error(request, "erreur d'ajout du lien d'encadrement.")
            return redirect("admins")
# Modifier un utilisateur
def edit_user(request):
    if request.method == 'POST':
        print("Données reçues : ", request.POST)
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(UserProfile, id=user_id)
            user.nom = request.POST.get('nom')
            user.prenom = request.POST.get('prenom')
            user.birthday = request.POST.get('birthday')
            user.sexe = request.POST.get('sexe')
            user.email = request.POST.get('email')
            user.type = request.POST.get('type')
            user.realisation_linkedin = request.POST.get('realisation_linkedin')
            if 'photo_profil' in request.FILES:
                user.photo_profil = request.FILES.get('photo_profil')
            if request.POST.get('password'):
                user.password = make_password(request.POST.get('password'))
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Utilisateur modifié avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

# Modifier un mémoire
def edit_memoire(request):
    if request.method == 'POST':
        try:
            memoire_id = request.POST.get('memoire_id')
            memoire = get_object_or_404(Memoire, id=memoire_id)
            memoire.titre = request.POST.get('titre')
            memoire.domaine = request.POST.get('domaine')
            memoire.annee_publication = request.POST.get('annee_publication')
            memoire.resume = request.POST.get('resume')
            if 'lien_telecharger' in request.FILES:
                
                memoire.fichier_memoire = request.FILES.get('lien_telecharger')
                print(memoire.fichier_memoire)
            if 'images' in request.FILES:
                memoire.images = request.FILES.get('images')
                print(memoire.images)
            auteur_id = request.POST.get('auteur')
            memoire.auteur = get_object_or_404(UserProfile, id=auteur_id)
            memoire.save()
            return JsonResponse({'status': 'success', 'message': 'Mémoire modifié avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
def edit_domaine(request):
    if request.method == 'POST':
        try:
            domaine_id = request.POST.get('domaine_id')
            domaine = get_object_or_404(Domaine, id=domaine_id)
            domaine.nom = request.POST.get('nom')

            domaine.save()
            return JsonResponse({'status': 'success', 'message': 'domaine modifié avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})        

# Modifier un encadrement
def edit_encadrement(request):
    if request.method == 'POST':
        try:
            encadrement_id = request.POST.get('encadrement_id')
            print(encadrement_id)
            encadrement = get_object_or_404(Encadrement, id=encadrement_id)
            memoire_id = request.POST.get('memoire')
            encadrant_id = request.POST.get('encadrant')
            print(memoire_id,encadrant_id)
            encadrement.memoire = get_object_or_404(Memoire, id=memoire_id)
            encadrement.encadrant = get_object_or_404(UserProfile, id=encadrant_id)
            encadrement.save()
            return JsonResponse({'status': 'success', 'message': 'Encadrement modifié avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def verification_page(request):
    if request.method == 'POST':
        # Récupération des données de session et du code saisi
        user_email = request.session.get('user_email')
        stored_code = request.session.get('verification_code')
        input_code = request.POST.get('verification_code')
        print(stored_code)

        # Vérification que les données de session existent
        if not user_email or not stored_code:
            messages.error(request, "Aucun utilisateur en attente de vérification.")
            return redirect('/register')

        # Vérification des codes
        if input_code == str(stored_code):
            try:
                # Marquer l'utilisateur comme vérifié (s'il y a un champ `is_verified` dans votre modèle)
                user = UserProfile.objects.get(email=user_email)
                user.is_verified = True  # Supposons qu'un champ `is_verified` existe
                user.save()

                # Supprimer les données de session
                del request.session['verification_code']
                del request.session['user_email']

                messages.success(request, "Votre compte a été vérifié avec succès.")
                return redirect('/login')  # Redirigez vers la page de connexion
            except UserProfile.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
                return redirect('/register')
        else:
            messages.error(request, "Code de vérification incorrect.")
            return redirect('/verification_page')  # Rechargez la page de vérification

    return render(request, 'verified.html')  # Chargez le template pour saisir le code
def verification_Email(request):
    if request.method == 'POST':
        # Récupération des données de session et du code saisi
        
       
        try:
            user_email =request.POST.get('email')
            request.session['emailv'] = user_email
            user = UserProfile.objects.get(email=user_email)
            
            
            
        
            if user.type == "admin" or user.type == "superadmin" :
                
            
                return redirect("login")
            else:
                 visiteur.objects.create(emailv=user_email)
                 
                 return redirect("liste_memoires")
        
        except :
            visiteur.objects.create(emailv=user_email)
            return redirect("liste_memoires/")      
        

       

    return render(request, 'conection.html')  # Chargez le template pour saisir le code
def telecharger_pdf(request):

    
    if request.method == "POST":
        try:
            idm = request.POST.get('memoire_id')
            
            emails=request.session.get('emailv')
            me = get_object_or_404(Memoire, id=idm)
            print(f"Le mémoire avec l'ID {emails} a été téléchargé.")
            telechargement.objects.create(memoire=me,emailt=emails)
            return redirect("liste_memoires/")
        except:
            return redirect("liste_memoires/")
    else:
        return redirect("liste_memoires/")
from django.db.models import Count    
# Vue pour obtenir la répartition des utilisateurs par type


from django.shortcuts import render
from datetime import datetime
from .utils import *

def send_welcome_email(request, *args, **kwargs):
    ctx={}
    
    if request.method == "POST":
        subjet='verification code '
        email=request.POST.get("email")
        # Génération du code de vérification à 6 chiffres
        verification_code = random.randint(100000, 999999)
        request.session['verification_code'] = verification_code
        request.session['user_email'] = email  
        
        user = UserProfile.objects.get(email=email)
        template='template.html'
        context={
            'date':datetime.today().date,
            'email':email,
            'user':user,
            'verification_code':verification_code,
            
            
                 }
        receivers=[email]
        has_send=send_advanced_email(recipient =receivers, subject=subjet, template=template, context=context)
        if has_send:
            ctx={ 'messages':"Mail envoyes avec success ,consulter votre boite email."}
            return redirect('/verification_page')
        ctx={ 'messages':'ERREUR d envoie du mails .'}
    return render(request,"verified.html",ctx) 
