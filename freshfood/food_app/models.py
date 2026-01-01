from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    CATEGORIE_CHOICES = (
        ('vf', 'viancde fraiche'),
        ('leg', 'legume'),
        ('sec', 'produit sec'),
        ('fru', 'fruit'),
        ('aut', 'autre'),
    )
    label = models.CharField(max_length=100)
    Categorie = models.CharField(choices=CATEGORIE_CHOICES, max_length=50, default='aut')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Changement: Utiliser DecimalField pour la monnaie
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label
    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client_name if self.client_name else f"Order {self.id}"

    # NOUVELLE MÉTHODE: Calcule le prix total de la commande
    def get_total_price(self):
        """Calcule le prix total en sommant les sous-totaux de tous les articles."""
        total = sum(article.get_subtotal() for article in self.orderarticle_set.all())
        return total

class OrderArticle(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.label}"

    # NOUVELLE MÉTHODE: Calcule le sous-total de cet article
    def get_subtotal(self):
        """Calcule le sous-total: quantité * prix du produit au moment de la commande (actuel ici)."""
        # Dans un scénario réel, vous devriez stocker le prix au moment de l'achat dans OrderArticle.
        # Ici, nous utilisons le prix actuel du produit.
        return self.quantity * self.product.price
    
    # PROPRIÉTÉ: Pour simuler l'accès à l'unit_price dans le template
    @property
    def unit_price(self):
        return self.product.price