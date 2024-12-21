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


def register_user(request):
    if request.method == 'POST':
        # Récupération des données
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        birthday = request.POST.get('birthday')
        sexe = request.POST.get('sexe')
        user_type = request.POST.get('type')
        realisation_linkedin = request.POST.get('realisation_linkedin', None)
        photo_profil = request.FILES.get('photo_profil', None)
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation des mots de passe
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('/register')

        # Vérification si l'utilisateur existe déjà
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Un utilisateur avec cet email existe déjà.")
            return redirect('/register')

        # Vérification si l'utilisateur non vérifié existe déjà
        if UnverifiedUserProfile.objects.filter(email=email).exists():
            messages.error(request, "Vous avez déjà initié une inscription. Vérifiez votre e-mail.")
            return redirect('/register')

        try:
            # Génération du code de vérification
            verification_code = random.randint(100000, 999999)

            # Enregistrement dans le modèle temporaire
            hashed_password = make_password(password)
            unverified_user = UnverifiedUserProfile.objects.create(
                nom=nom,
                prenom=prenom,
                email=email,
                birthday=birthday,
                sexe=sexe,
                type=user_type,
                realisation_linkedin=realisation_linkedin,
                photo_profil=photo_profil,
                password=hashed_password,
                verification_code=str(verification_code),
            )

            # Enregistrer les informations dans la session
            request.session['user_email'] = email
            request.session['verification_code'] = verification_code
            request.session['user_id'] = unverified_user.id  # Ajout de l'ID utilisateur dans la session

            # Envoi de l'email avec le code de vérification
            subject = "Code de vérification"
            template = "template.html"
            context = {
                'verification_code': verification_code,
                'user': unverified_user,
            }
            send_advanced_email([email], subject, template, context)

            messages.success(request, "Un code de vérification vous a été envoyé par email.")
            return render(request, "verified.html", context)

        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            return redirect('/register')

    return render(request, "register.html")


def verification_page(request):
    # Vérifier la présence de l'ID de l'utilisateur dans la session
    email = request.session.get('user_email')
    stored_code = request.session.get('verification_code')

    if not email or not stored_code:
        return redirect('register')  # Si les informations sont manquantes, rediriger vers l'inscription

    try:
        # Tenter de récupérer l'utilisateur non vérifié
        unverified_user = UnverifiedUserProfile.objects.get(email=email)
    except UnverifiedUserProfile.DoesNotExist:
        return HttpResponse("Utilisateur non trouvé.", status=404)

    if request.method == "POST":
        verification_code = request.POST.get('verification_code')

        if verification_code == str(stored_code):
            # Création de l'utilisateur vérifié
            user = UserProfile.objects.create(
                nom=unverified_user.nom,
                prenom=unverified_user.prenom,
                email=unverified_user.email,
                birthday=unverified_user.birthday,
                sexe=unverified_user.sexe,
                type=unverified_user.type,
                realisation_linkedin=unverified_user.realisation_linkedin,
                photo_profil=unverified_user.photo_profil,
                password=unverified_user.password,
            )

            # Connexion automatique de l'utilisateur
            login(request, user)

            # Suppression de l'utilisateur non vérifié
            unverified_user.delete()

            messages.success(request, "Votre compte a été vérifié et vous êtes maintenant connecté.")
            return redirect('login')  # Redirigez vers la page d'accueil ou une page personnalisée

        else:
            # Code de vérification incorrect
            return render(request, "verified.html", {"error": "Code de vérification incorrect."})

    # Si GET, afficher la page de vérification
    return render(request, "verified.html")
def resend_email(request, *args, **kwargs):
    # Récupérer l'email de la session
    email = request.session.get('user_email')
    
    if not email:
        # Si l'email n'est pas trouvé dans la session, rediriger l'utilisateur
        messages.error(request, "Aucune session utilisateur active.")
        return redirect('login')  # Remplacez 'login' par l'URL appropriée

    try:
        # Génération d'un nouveau code de vérification
        verification_code = random.randint(100000, 999999)
        request.session['verification_code'] = verification_code

        # Récupérer l'utilisateur non vérifié à partir de l'email
        unverified_user = UnverifiedUserProfile.objects.get(email=email)

        # Envoi de l'email avec le code de vérification
        subject = "Code de vérification"
        template = "template.html"  # Assurez-vous que ce template existe
        context = {
            'verification_code': verification_code,
            'user': unverified_user,
        }

        send_advanced_email([email], subject, template, context)

        # Message de succès et redirection vers la page de vérification
        messages.success(request, "Un code de vérification vous a été envoyé par email.")
        return render(request, "verified.html", context)

    except UnverifiedUserProfile.DoesNotExist:
        # Gestion de l'erreur si l'utilisateur n'est pas trouvé dans la base de données
        messages.error(request, "Aucun utilisateur trouvé avec cet email.")
        return redirect('/register')  # Rediriger vers la page d'inscription ou une page d'erreur

    except Exception as e:
        # Gestion de toutes autres erreurs
        messages.error(request, f"Une erreur est survenue : {str(e)}")
        return redirect('register')

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
                    visiteur.objects.create(emailv=email)
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
        # Vérification de l'authentification
        idp = request.session['user_id']
        user = UserProfile.objects.get(id=idp)
    except KeyError:
        return redirect('logout')
    
   
    
    try:
        # Récupération des mémoires avec toutes leurs relations
        memoires = Memoire.objects.prefetch_related(
            Prefetch(
                'encadrements',
                queryset=Encadrement.objects.select_related('encadrant'),
                to_attr='encadreur_list'
            ),
            'domaines',
            Prefetch(
                'notations',
                queryset=NotationCommentaire.objects.select_related('utilisateur'),
                to_attr='notations_list'
            ),
            'telechargements'
        ).select_related(
            'auteur'
        ).annotate(
            nbr_telechargements=Count('telechargements'),
            note_moyenne=Avg('notations__note'),
            nbr_notations=Count('notations'),
            nbr_commentaires=Count('notations')  # Vérifiez que cela compte correctement
        )

        # Recherche textuelle
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

        # Construction du dictionnaire détaillé pour la liste de mémoires
        memoires_list = []
        for memoire in memoires:
            memoires_list.append({
                'id': memoire.id,
                'titre': memoire.titre,
                'annee_publication': memoire.annee_publication,
                'resume': memoire.resume,
                'auteur': {
                    'id': memoire.auteur.id,
                    'nom': memoire.auteur.nom,
                    'prenom': memoire.auteur.prenom,
                    'email': memoire.auteur.email,
                    'photo_profil': memoire.auteur.photo_profil.url if memoire.auteur.photo_profil else None,
                    'linkedin': memoire.auteur.realisation_linkedin
                },
                'domaines': [{
                    'id': domaine.id,
                    'nom': domaine.nom
                } for domaine in memoire.domaines.all()],
                'encadreurs': [{
                    'id': encadrement.encadrant.id,
                    'nom': encadrement.encadrant.nom,
                    'prenom': encadrement.encadrant.prenom,
                    'email': encadrement.encadrant.email,
                    'photo_profil': encadrement.encadrant.photo_profil.url if encadrement.encadrant.photo_profil else None,
                    'linkedin': encadrement.encadrant.realisation_linkedin
                } for encadrement in memoire.encadreur_list],
                'statistiques': {
                    'nbr_telechargements': memoire.nbr_telechargements,
                    'note_moyenne': round(memoire.note_moyenne, 2) if memoire.note_moyenne else 0,
                    'nbr_notations': memoire.nbr_notations,
                    'nbr_commentaires': memoire.nbr_commentaires  # Nombre de commentaires
                },
                'notations': [{
                    'utilisateur': {
                        'id': notation.utilisateur.id,
                        'nom': notation.utilisateur.nom,
                        'prenom': notation.utilisateur.prenom,
                        'linkedin': notation.utilisateur.realisation_linkedin,
                        'photo_profil': notation.utilisateur.photo_profil.url if notation.utilisateur.photo_profil else None
                    },
                    'note': notation.note,
                    'commentaire': notation.commentaire,
                    'date': notation.date_creation
                } for notation in memoire.notations_list],
                'telechargements': [{
                    'email': telechargement.emailt,
                    'date': telechargement.datet
                } for telechargement in memoire.telechargements.all()],
                'fichiers': {
                    'image': memoire.images.url if memoire.images else None,
                    'document': memoire.fichier_memoire.url if memoire.fichier_memoire else None
                }
            })

        # Données pour les filtres
        domaines_uniques = Domaine.objects.all()
        annees_uniques = Memoire.objects.values_list('annee_publication', flat=True).distinct()
        encadreurs_uniques = UserProfile.objects.filter(encadrements__isnull=False).distinct()
        auteurs_uniques = UserProfile.objects.filter(memoires__isnull=False).distinct()

        context = {
            'memoires': memoires_list,
            'domaines': domaines_uniques,
            'annees': sorted(annees_uniques),
            'encadreurs': encadreurs_uniques,
            'auteurs': auteurs_uniques,
            'query_params': request.GET,
            'user': user
        }

        return render(request, 'memoire.html', context)

    except Exception as e:
        messages.error(request, f"Une erreur s'est produite: {str(e)}")
        return redirect('liste_memoires')

def common(request,*args, **kwargs):
   

    return render(request, 'index.html')

  

def ajouter_commentaire(request, memoire_id):
    # Vérification de l'authentification
    if not request.user.is_authenticated:
        return redirect('login')  # Redirige l'utilisateur vers la page de connexion s'il n'est pas authentifié

    try:
        # Vérification de l'authentification
        idp = request.session['user_id']
    except KeyError:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)# Récupérer le profil de l'utilisateur connecté

    # Récupérer le mémoire concerné
    memoire = get_object_or_404(Memoire, id=memoire_id)

    # Vérifier si l'utilisateur a déjà commenté ce mémoire
    if NotationCommentaire.objects.filter(memoire=memoire, utilisateur=user).exists():
        messages.error(request, "Vous avez déjà commenté ce mémoire.")
        return redirect('liste_memoires')

    if request.method == 'POST':
        # Récupérer les données du formulaire
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire')

        # Ajouter un nouveau commentaire et une note
        notation = NotationCommentaire(
            memoire=memoire,
            utilisateur=user,
            note=note,
            commentaire=commentaire
        )
        notation.save()

        messages.success(request, "Votre commentaire et note ont été ajoutés avec succès.")
        return redirect('liste_memoires')

    return redirect('liste_memoires')
    
    
   
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
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)
    
    if request.method == 'POST':
        memoire_id = request.POST.get('memoire_id')
        try:
            memoire = get_object_or_404(Memoire, id=memoire_id)

            # Préparer les détails pour l'email
            object_before = {
                "id": memoire.id,
                "titre": memoire.titre,
                "auteur": f"{memoire.auteur.nom} {memoire.auteur.prenom}",
                "annee_publication": memoire.annee_publication
            }

            # Supprimer le mémoire
            memoire.delete()

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Suppression d'un mémoire",
                action_type="Suppression",
                action_details=f"Le mémoire avec l'ID: {memoire_id} a été supprimé.",
                object_before=object_before,  # Etat avant suppression
                object_after=None  # Pas d'état après suppression
            )

            return JsonResponse({'status': 'success', 'message': 'Mémoire supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
def delete_comment(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)
    
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        
        try:
            comment = get_object_or_404(NotationCommentaire, id=comment_id)

            # Préparer les détails pour l'email
            object_before = {
                "id": comment.id,
                "commentaire": comment.commentaire,
                "utilisateur": f"{comment.utilisateur.nom} {comment.utilisateur.prenom}"
            }

            # Supprimer le commentaire
            comment.delete()

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Suppression d'un commentaire",
                action_type="Suppression",
                action_details=f"Le commentaire avec l'ID: {comment_id} a été supprimé.",
                object_before=object_before,  # Etat avant suppression
                object_after=None  # Pas d'état après suppression
            )

            return JsonResponse({'status': 'success', 'message': 'Commentaire supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
def delete_domaine(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)
    
    if request.method == 'POST':
        domaine_id = request.POST.get('domaine_id')
        try:
            domaine = get_object_or_404(Domaine, id=domaine_id)

            # Préparer les détails pour l'email
            object_before = {
                "id": domaine.id,
                "nom": domaine.nom
            }

            # Supprimer le domaine
            domaine.delete()

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Suppression d'un domaine",
                action_type="Suppression",
                action_details=f"Le domaine avec l'ID: {domaine_id} a été supprimé.",
                object_before=object_before,  # Etat avant suppression
                object_after=None  # Pas d'état après suppression
            )

            return JsonResponse({'status': 'success', 'message': 'Domaine supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
  

# Supprimer un utilisateur
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = get_object_or_404(UserProfile, id=user_id)
            user_name = f"{user.nom} {user.prenom}"  # Récupérer le nom complet de l'utilisateur

            # Supprimer l'utilisateur
            user.delete()

            # Préparer les détails pour l'email
            object_before = {
                "id": user.id,
                "nom": user.nom,
                "prenom": user.prenom,
                "email": user.email,
                "type": user.type,
                "linkdin":user.realisation_linkedin,
                "password":user.password,
                "sex":user.sexe,
                    "birthday":user.birthday
                
            }

            send_admin_email(
                user=request.user,  # L'utilisateur qui a effectué l'action
                subject="Suppression d'un utilisateur",
                action_type="Suppression",
                action_details=f"L'utilisateur '{user_name}' avec l'ID: {user_id} a été supprimé.",
                object_before=object_before,  # Etat avant suppression
                object_after=None  # Pas d'état après suppression
            )

            messages.success(request, 'Utilisateur supprimé avec succès.')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de l'utilisateur : {str(e)}")
        return redirect('admins')
def delete_encadrement(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')

    user = UserProfile.objects.get(id=idp)  # Utilisateur qui effectue l'action

    if request.method == 'POST':
        encadrement_id = request.POST.get('encadrement_id')
        try:
            encadrement = get_object_or_404(Encadrement, id=encadrement_id)

            # Préparer les détails pour l'email
            object_before = {
                "memoire_id": encadrement.memoire.id,
                "encadrant": f"{encadrement.encadrant.nom} {encadrement.encadrant.prenom}",
                "encadrant_email": encadrement.encadrant.email
            }

            # Supprimer l'encadrement
            encadrement.delete()

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Suppression d'un encadrement",
                action_type="Suppression",
                action_details=f"L'encadrement avec l'ID: {encadrement_id} a été supprimé.",
                object_before=object_before,  # Etat avant suppression
                object_after=None  # Pas d'état après suppression
            )

            return JsonResponse({'status': 'success', 'message': 'Encadrement supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
def add_user(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')

    user = UserProfile.objects.get(id=idp)  # Utilisateur qui effectue l'action

    if request.method == 'POST':
        try:
            # Créer un nouvel utilisateur
            new_user = UserProfile.objects.create(
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

            # Préparer les détails pour l'email
            object_after = {
                "id": new_user.id,
                "nom": new_user.nom,
                "prenom": new_user.prenom,
                "email": new_user.email,
                "type": new_user.type,
                "linkdin":new_user.realisation_linkedin,
                "password":new_user.password,
                "sex":new_user.sexe,
                    "birthday":new_user.birthday
            }

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Ajout d'un utilisateur",
                action_type="Ajout",
                action_details=f"L'utilisateur '{new_user.nom} {new_user.prenom}' a été créé avec le rôle '{new_user.type}'.",
                object_before=None,  # Pas d'état avant création
                object_after=object_after  # Détails du nouvel utilisateur
            )

            messages.success(request, 'Utilisateur ajouté avec succès.')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout de l'utilisateur : {str(e)}")
        return redirect('admins')


# Ajouter un mémoire
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Memoire, Domaine, UserProfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Memoire, Domaine, UserProfile

def add_memoire(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')

    user = UserProfile.objects.get(id=idp)  # Utilisateur qui effectue l'action

    if request.method == 'POST':
        try:
            auteur_id = request.POST.get('auteur')
            auteur = get_object_or_404(UserProfile, id=auteur_id)

            # Récupérer les domaines sélectionnés
            domaines_ids = request.POST.getlist('domaines')
            domaines = Domaine.objects.filter(id__in=domaines_ids)

            # Récupérer les fichiers envoyés
            fichier_memoire = request.FILES.get('lien_telecharger')
            image = request.FILES.get('images')

            # Création de l'objet Memoire
            memoire = Memoire.objects.create(
                titre=request.POST.get('titre'),
                annee_publication=request.POST.get('annee_publication'),
                images=image,
                auteur=auteur,
                resume=request.POST.get('resume'),
                fichier_memoire=fichier_memoire
            )
            
            # Associer les domaines au mémoire
            memoire.domaines.set(domaines)
            memoire.save()

            # Préparer les détails pour l'email
            object_after = {
                "id": memoire.id,
                "titre": memoire.titre,
                "annee_publication": memoire.annee_publication,
                "auteur": f"{auteur.nom} {auteur.prenom}",
                "domaines": [d.nom for d in domaines],
                "resume": memoire.resume
            }

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Ajout d'un mémoire",
                action_type="ajout",
                action_details=f"Le mémoire '{memoire.titre}' a été ajouté avec succès.",
                object_before=None,  # Pas d'état initial
                object_after=object_after
            )

            messages.success(request, "Mémoire ajouté avec succès.")
            return redirect("admins")

        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout du mémoire : {str(e)}")
            return redirect("admins")
def add_domaine(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')

    user = UserProfile.objects.get(id=idp)  # Utilisateur qui effectue l'action

    if request.method == 'POST':
        try:
            nom = request.POST.get('nom')

            # Création de l'objet Domaine
            domaine = Domaine.objects.create(
                nom=nom
            )

            # Préparer les détails pour l'email
            object_after = {
                "id": domaine.id,
                "nom": domaine.nom
            }

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Ajout d'un domaine",
                action_type="ajout",
                action_details=f"Le domaine '{domaine.nom}' a été ajouté avec succès.",
                object_before=None,  # Pas d'état initial
                object_after=object_after
            )

            messages.success(request, "Domaine ajouté avec succès.")
            return redirect("admins")

        except Exception as e:
            messages.error(request, f"Erreur d'ajout du domaine : {str(e)}")
            return redirect("admins")


# Ajouter un encadrement
def add_encadrement(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    
    user = UserProfile.objects.get(id=idp)  # Utilisateur qui effectue l'action
    
    if request.method == 'POST':
        try:
            memoire_id = request.POST.get('memoire')
            encadrant_id = request.POST.get('encadrant')

            # Récupérer les objets Mémoire et Encadrant
            memoire = get_object_or_404(Memoire, id=memoire_id)
            encadrant = get_object_or_404(UserProfile, id=encadrant_id)

            # Créer l'encadrement
            encadrement = Encadrement.objects.create(memoire=memoire, encadrant=encadrant)

            # Préparer les données pour l'email
            object_after = {
                "id": encadrement.id,
                "memoire_id": memoire.id,
                "memoire_titre": memoire.titre,
                "encadrant_id": encadrant.id,
                "encadrant_nom": f"{encadrant.nom} {encadrant.prenom}",
            }

            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Ajout d'un encadrement",
                action_type="ajout",
                action_details=f"L'encadrement pour la mémoire '{memoire.titre}' a été ajouté avec succès.",
                object_before=None,  # Pas d'état avant l'ajout, car c'est une création
                object_after=object_after,
            )

            messages.success(request, "Encadrement ajouté avec succès.")
            return redirect("admins")
        
        except Exception as e:
            messages.error(request, f"Erreur d'ajout de l'encadrement : {str(e)}")
            return redirect("admins")

# Modifier un utilisateur
def edit_user(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    admin_user = UserProfile.objects.get(id=idp)  # Utilisateur qui effectue l'action

    if request.method == 'POST':
        print("Données reçues : ", request.POST)
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(UserProfile, id=user_id)

            # Capturer l'état de l'objet avant modification
            object_before = vars(user).copy()

            # Mettre à jour les champs
            user.nom = request.POST.get('nom')
            user.prenom = request.POST.get('prenom')
            user.birthday = request.POST.get('birthday')
            user.sexe = request.POST.get('sexe')
            user.email = request.POST.get('email')
            user.type = request.POST.get('type')
            user.realisation_linkedin = request.POST.get('realisation_linkedin')

            # Mettre à jour la photo de profil (si présente)
            if 'photo_profil' in request.FILES:
                user.photo_profil = request.FILES.get('photo_profil')

            # Mettre à jour le mot de passe (si présent)
            if request.POST.get('password'):
                user.password = make_password(request.POST.get('password'))

            # Sauvegarder l'utilisateur modifié
            user.save()

            # Capturer l'état de l'objet après modification
            object_after = vars(user)

            # Envoyer un email avec les détails
            send_admin_email(
                user=admin_user,  # L'utilisateur qui a effectué l'action
                subject="Modification d'un utilisateur",
                action_type="modification",
                action_details=f"L'utilisateur {user.nom} {user.prenom} a été modifié avec succès.",
                object_before=object_before,
                object_after=object_after,
            )

            return JsonResponse({'status': 'success', 'message': 'Utilisateur modifié avec succès.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


# Modifier un mémoire
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Memoire, UserProfile, Domaine
from django.core.exceptions import ValidationError

def edit_memoire(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    user = UserProfile.objects.get(id=idp)

    if request.method == 'POST':
        try:
            memoire_id = request.POST.get('memoire_id')
            memoire = get_object_or_404(Memoire, id=memoire_id)

            # Capturer l'état de l'objet avant modification
            object_before = vars(memoire).copy()

            # Mettre à jour les champs
            memoire.titre = request.POST.get('titre')
            memoire.annee_publication = request.POST.get('annee_publication')
            memoire.resume = request.POST.get('resume')

            # Mettre à jour l'image (si présente)
            if 'images' in request.FILES:
                memoire.images = request.FILES.get('images')

            # Mettre à jour le fichier du mémoire (si présent)
            if 'lien_telecharger' in request.FILES:
                memoire.fichier_memoire = request.FILES.get('lien_telecharger')

            # Mettre à jour l'auteur
            auteur_id = request.POST.get('auteur')
            memoire.auteur = get_object_or_404(UserProfile, id=auteur_id)

            # Mettre à jour les domaines associés au mémoire
            domaines_ids = request.POST.getlist('domaines')  # Liste des domaines sélectionnés
            domaines = Domaine.objects.filter(id__in=domaines_ids)  # Récupérer les domaines sélectionnés
            memoire.domaines.set(domaines)  # Mettre à jour la relation ManyToMany

            # Sauvegarder le mémoire modifié
            memoire.save()

            # Capturer l'état de l'objet après modification
            object_after = vars(memoire)

            # Envoyer un email avec les détails
            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Modification d'un mémoire",
                action_type="modification",
                action_details=f"Le mémoire avec l'ID {memoire_id} a été modifié avec succès.",
                object_before=object_before,
                object_after=object_after,
            )

            return JsonResponse({'status': 'success', 'message': 'Mémoire modifié avec succès.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


def edit_domaine(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    user = UserProfile.objects.get(id=idp)
    
    if request.method == 'POST':
        try:
            domaine_id = request.POST.get('domaine_id')
            domaine = get_object_or_404(Domaine, id=domaine_id)
            
            # Capturer l'état de l'objet avant modification
            object_before = vars(domaine).copy()
            
            # Appliquer les modifications
            domaine.nom = request.POST.get('nom')
            
            # Sauvegarder les modifications
            domaine.save()
            
            # Capturer l'état de l'objet après modification
            object_after = vars(domaine)
            
            # Envoyer un email avec les détails
            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Modification d'un domaine",
                action_type="modification",
                action_details=f"Le domaine avec l'ID {domaine_id} a été modifié avec succès.",
                object_before=object_before,
                object_after=object_after,
            )
            return JsonResponse({'status': 'success', 'message': 'Domaine modifié avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

# Modifier un encadrement
def edit_encadrement(request):
    try:
        idp = request.session['user_id']
    except:
        return redirect('logout')
    user = UserProfile.objects.get(id=idp)
    
    if request.method == 'POST':
        try:
            encadrement_id = request.POST.get('encadrement_id')
            print(encadrement_id)
            encadrement = get_object_or_404(Encadrement, id=encadrement_id)
            
            # Capturer l'état de l'objet avant modification
            object_before = vars(encadrement).copy()
            
            # Récupérer les nouvelles données du formulaire
            memoire_id = request.POST.get('memoire')
            encadrant_id = request.POST.get('encadrant')
            
            # Appliquer les modifications
            encadrement.memoire = get_object_or_404(Memoire, id=memoire_id)
            encadrement.encadrant = get_object_or_404(UserProfile, id=encadrant_id)
            
            # Sauvegarder les modifications
            encadrement.save()
            
            # Capturer l'état après modification
            object_after = vars(encadrement)
            
            # Envoyer l'email
            send_admin_email(
                user=user,  # L'utilisateur qui a effectué l'action
                subject="Modification d'un encadrement",
                action_type="modification",
                action_details=f"L'encadrement avec l'ID {encadrement_id} a été modifié avec succès.",
                object_before=object_before,
                object_after=object_after,
            )
            return JsonResponse({'status': 'success', 'message': 'Encadrement modifié avec succès.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


from django.shortcuts import render, redirect
from django.http import HttpResponse


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
    return render(request, "verified.html")     
        

       

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
            'date':datetime.today().date(),
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
from datetime import datetime
def send_admin_email(user, subject, action_type, action_details,object_before,object_after):
    print(user) 
    # Récupère tous les utilisateurs ayant le rôle d'admin ou superadmin
    admins = UserProfile.objects.filter(type="superadmin") | UserProfile.objects.filter(type="admin")
    recipients = [admin.email for admin in admins if admin.email]  # S'assurer que l'email est valide

    # Préparer le contexte pour le template de l'email
    context = {
        'action_type': action_type,  # Type d'action
        'action_details': action_details, 
        'user':user,# Détails de l'action

        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'object_before': object_before,
        'object_after': object_after,
    }
    
    if recipients:
        send_advanced_email(
            recipient=recipients,
            subject=subject,
            template='adminmail.html',
            context=context
        )
       