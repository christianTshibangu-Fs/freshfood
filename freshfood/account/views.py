from django.shortcuts import render
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
# Create your views here.

# Vue d'inscription personnalisée
def register(request):
    """Gère l'inscription de nouveaux utilisateurs."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connecte l'utilisateur immédiatement après l'inscription
            login(request, user)
            # Redirige vers la page d'accueil ou une autre page après l'inscription
            return redirect('/') 
    else:
        form = UserCreationForm()
    
    # Rend le template 'register.html' en passant le formulaire
    return render(request, 'account/register.html', {'form': form})

@login_required
def profile(request):

    if request.method == 'POST':
        # On instancie les formulaires avec les données envoyées (request.POST) 
        # et les fichiers (request.FILES pour l'image)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, 
                                   instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Votre compte a été mis à jour !')
            return redirect('profile') # Redirection pour éviter la resoumission du formulaire (Post/Redirect/Get pattern)

    else:
        # Requête GET : On pré-remplit les formulaires avec les infos actuelles de l'utilisateur
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'blog/profile.html', context)


