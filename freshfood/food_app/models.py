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
    price = models.PositiveIntegerField()
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

class OrderArticle(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.label}"