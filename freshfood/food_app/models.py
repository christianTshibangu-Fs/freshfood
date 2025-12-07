from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Product(models.Model):
    CATEGORIE_CHOICES = (
        ('Admin', 'Admin'),
        ('Librarian', 'Bibliothécaire'),
        ('Member', 'Membre'),
    )
    label = models.CharField(max_length=100)
    Categorie = CATEGORIE_CHOICES
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class OrderArticle(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.label}"