from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, FormView, TemplateView, RedirectView
from .models import Product, Order, OrderArticle
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 
from django.contrib.auth.decorators import  login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest


# Create your views here.
class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin qui vérifie si l'utilisateur est connecté ET est un administrateur (is_staff ou is_superuser).
    
    Si le test échoue (non-admin), l'utilisateur est redirigé vers la page de connexion.
    """
    
    # URL de connexion par défaut si non spécifiée
    login_url = reverse_lazy('login') 

    def test_func(self):
        user = self.request.user
        # L'utilisateur doit être authentifié ET avoir le statut 'is_staff' ou 'is_superuser'.
        return user.is_authenticated and (user.is_superuser or user.is_staff)

    def handle_no_permission(self):
        # Surcharge pour forcer la redirection vers la page de connexion
        return redirect(self.get_login_url())

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
    return render(request, 'food_app/register.html', {'form': form})


def index(request):
    return render(request, 'food_app/indexe.html')

#### Product Views ###
# Create view for a new product
class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    fields = ['label', 'description', 'price', 'Categorie']
    template_name = 'food_app/product_form.html'
    success_url = '/products/'
    redirect_field_name = 'food_app/product_list.html'

# List view for all products
class ProductListView(ListView):
    model = Product
    ordering = ["label"]
    template_name = 'food_app/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Les produits de la page courante (grâce à la pagination)
        all_products_on_page = context['object_list'] 
        
        # Récupérer la correspondance code -> label (ex: 'vf' -> 'viancde fraiche')
        category_map = dict(Product.CATEGORIE_CHOICES)
        
        categorized_products = {}
        
        # Regrouper les produits par leur nom de catégorie lisible
        for product in all_products_on_page:
            # Utiliser le code (ex: 'vf') pour trouver le libellé ('viancde fraiche')
            category_code = product.Categorie
            category_label = category_map.get(category_code, 'Catégorie Inconnue')
            
            if category_label not in categorized_products:
                categorized_products[category_label] = []
                
            categorized_products[category_label].append(product)
            
        # Ajouter le dictionnaire groupé au contexte
        # Trier par nom de catégorie pour un affichage cohérent
        sorted_categorized_products = dict(sorted(categorized_products.items()))
        context['categorized_products'] = sorted_categorized_products
        
        return context

# Detail view for a single product
@method_decorator(login_required, name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    template_name = 'food_app/product_detail.html'
    context_object_name = 'product'

# Update view for editing a product
class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    fields = ['label', 'description', 'price', 'Categorie']
    template_name = 'food_app/product_update_form.html'
    success_url = '/products/'

# Delete view for removing a product
class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'food_app/product_confirm_delete.html'
    success_url = '/products/'

# Search view for products by label
class ProductSearchView(ListView):
    model = Product
    template_name = 'food_app/product_search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(label__icontains=query)
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context 

# View for products by category
class ProductByCategoryView(ListView):
    model = Product
    template_name = 'food_app/product_by_category.html'

    def get_queryset(self):
        category = self.kwargs.get('category')
        return Product.objects.filter(category__name__iexact=category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs.get('category', '')
        return context

### Order Views ###   

# Create view for a new order
@method_decorator(login_required, name='dispatch') # Ceci est maintenant redondant
class OrderCreateView(CreateView):
    model = Order
    fields = ['client_name']
    template_name = 'food_app/order_form.html'
    success_url = '/order-articles/new/'


# List view for all orders
class OrderedListView(AdminRequiredMixin, ListView):
    model = Order
    ordering = ['-created_at']
    template_name = 'food_app/ordered_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        """
        Optimise les requêtes pour éviter le problème N+1.
        - select_related pour le client (ForeignKey)
        - prefetch_related pour les articles de la commande (relation inverse)
        """
        
        # Le nom par défaut de la relation inverse de OrderArticle vers Order est 'orderarticle_set'.
        # Nous utilisons Prefetch pour charger les articles et leurs produits associés.
        order_articles_prefetch = Prefetch(
            'orderarticle_set',  # Le related_name par défaut de OrderArticle vers Order
            queryset=OrderArticle.objects.select_related('product'),
            to_attr='articles' # Nomme l'attribut de résultat 'articles' pour une utilisation facile dans le template
        )

        return Order.objects.all().select_related(
            'customer'  # Chargement de l'utilisateur (User)
        ).prefetch_related(
            order_articles_prefetch
        ).order_by('-created_at')

# Detail view for a single order
class OrderDetailView(AdminRequiredMixin, DetailView):
    model = Order
    template_name = 'food_app/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_articles'] = OrderArticle.objects.filter(order=self.object)
        return context
    
# Delete view for removing an order
class OrderDeleteView(AdminRequiredMixin, DeleteView):
    model = Order
    template_name = 'food_app/order_confirm_delete.html'
    success_url = '/orders/'    

# update view for editing an order
class OrderUpdateView(AdminRequiredMixin, UpdateView):
    model = Order
    fields = ['customer']
    template_name_suffix = '_update_form'
    success_url = '/orders/'


### Order Article Views ###

# Create view for adding articles to an order
@method_decorator(login_required, name='dispatch') # Ceci est maintenant redondant
class OrderArticleCreateView(CreateView):
    model = OrderArticle
    fields = ['product', 'quantity', 'order']
    template_name = 'food_app/orderarticle_form.html'
    success_url = '/order-articles/new/'

# Delete view for removing an order article
@method_decorator(login_required, name='dispatch') # Ceci est maintenant redondant
class OrderArticleDeleteView(DeleteView):
    model = OrderArticle
    template_name = 'food_app/orderarticle_confirm_delete.html'
    success_url = '/orders/'

# Update view for editing an order article
@method_decorator(login_required, name='dispatch') # Ceci est maintenant redondant
class OrderArticleUpdateView(UpdateView):   
    model = OrderArticle
    fields = ['product', 'quantity', 'order']
    template_name_suffix = '_update_form'
    success_url = '/orders/'

# List view for all order articles
@method_decorator(login_required, name='dispatch') # Ceci est maintenant redondant
class OrderArticleListView(ListView):
    model = OrderArticle
    ordering = ['order']
    template_name = 'food_app/orderarticle_list.html'
    context_object_name = 'order_articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

# Detail view for a single order article
@method_decorator(login_required, name='dispatch') # Ceci est maintenant redondant
class OrderArticleDetailView(DetailView):
    model = OrderArticle
    template_name = 'food_app/orderarticle_detail.html'
    context_object_name = 'order_article'   

# Pour cet exemple, nous allons simuler un utilisateur connecté.
# En production, vous utiliseriez @login_required.
DEFAULT_CUSTOMER_ID = 1


@method_decorator(login_required, name='dispatch')
class OrderView(View):
    template_name = 'food_app/order_form.html'

    def get(self, request, *args, **kwargs):
        """
        Affiche la liste des produits disponibles.
        """
        # Récupérer tous les produits avec leurs IDs et prix
        products = Product.objects.all().values('id', 'label', 'description', 'price')
        
        # Passer les données à la template (le reste du panier est géré par JS)
        context = {
            'products': list(products),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Traite la soumission du formulaire de commande (panier validé).
        """
        try:
            # 1. Récupérer les données de la requête
            # Les données doivent être envoyées en JSON depuis le JavaScript
            import json
            data = json.loads(request.body)
            
            client_name = data.get('client_name')
            cart_items = data.get('cart_items', [])
            user = request.user

            if not cart_items:
                return HttpResponseBadRequest("Le panier est vide.")
            
            # 2. Simuler l'utilisateur (à remplacer par request.user)
            # En réalité, l'utilisateur est request.user si vous utilisez @login_required
            try:
                customer = User.objects.get(pk=user.id)
            except User.DoesNotExist:
                # Créer un utilisateur par défaut si nécessaire pour le test
                customer = User.objects.create_user(
                    username='default_client', 
                    password='password', 
                    email='test@example.com'
                )


            # 3. Utiliser une transaction pour garantir l'atomicité
            with transaction.atomic():
                # Création de l'objet Order principal
                order = Order.objects.create(
                    customer=customer,
                    client_name=client_name or customer.username
                )

                # Dictionnaire pour valider les IDs de produits et les prix
                product_map = {
                    p.id: p for p in Product.objects.filter(id__in=[item['product_id'] for item in cart_items])
                }

                # Création des OrderArticle
                order_articles = []
                for item in cart_items:
                    product_id = item.get('product_id')
                    quantity = int(item.get('quantity', 0))

                    if quantity > 0 and product_id in product_map:
                        product = product_map[product_id]
                        
                        order_articles.append(
                            OrderArticle(
                                order=order,
                                product=product,
                                quantity=quantity
                            )
                        )
                
                # Enregistrement en masse des articles de la commande
                if not order_articles:
                    # Si aucune ligne valide, annuler la commande (rollback de la transaction)
                    raise ValueError("Aucun article valide trouvé dans le panier.")
                    
                OrderArticle.objects.bulk_create(order_articles)

            # 4. Réponse de succès
            return JsonResponse({'message': 'Commande enregistrée avec succès!', 'order_id': order.id}, status=201)

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Format de données JSON invalide.")
        except ValueError as e:
            # Gère l'erreur si aucun article valide n'a pu être créé
            return HttpResponseBadRequest(f"Erreur de validation: {e}")
        except Exception as e:
            # Gestion des autres erreurs (DB, etc.)
            return JsonResponse({'message': f'Erreur lors de l\'enregistrement: {e}'}, status=500)


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'food_app/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['total_orders'] = Order.objects.count()
        context['total_order_articles'] = OrderArticle.objects.count()
        context['recent_orders'] = Order.objects.order_by('-created_at')[:5]
        context['recent_products'] = Product.objects.order_by('-id')[:5]
        context['all_orders'] = Order.objects.all()
        context['all_products'] = Product.objects.all()

        return context

 
@method_decorator(login_required, name='dispatch')
class UserOrderListView(ListView):
    model = Order
    template_name = 'food_app/user_order_list.html'
    context_object_name = 'user_orders'

    def get_queryset(self):
        # Définition de la pré-récupération des articles de commande
        # On utilise le related_name par défaut 'orderarticle_set' et on charge les produits associés
        order_articles_prefetch = Prefetch(
            'orderarticle_set',  
            queryset=OrderArticle.objects.select_related('product'),
            to_attr='articles' # Nomme la liste d'articles dans le template : order.articles
        )

        # Récupérer uniquement les commandes de l'utilisateur connecté, 
        # optimiser le chargement et trier par date
        return Order.objects.filter(customer=self.request.user).select_related(
            'customer'
        ).prefetch_related(
            order_articles_prefetch
        ).order_by('-created_at')
    
    


