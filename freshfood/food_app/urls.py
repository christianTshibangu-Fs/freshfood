from django.urls import path
from .views import (
    home,
    ProductListView, ProductDetailView, ProductUpdateView, ProductDeleteView, ProductSearchView, ProductCreateView,
    OrderCreateView, OrderedListView, OrderDetailView, OrderUpdateView, OrderDeleteView,
    OrderArticleCreateView, OrderArticleListView, OrderArticleDetailView, OrderArticleUpdateView, OrderArticleDeleteView
)

urlpatterns = [
    path('', home, name='food_app-home'),  
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'), 
    path('products/new/', ProductCreateView.as_view(), name='product-create'),
    path('orders/', OrderedListView.as_view(), name='order-list'),
    path('orders/new/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order-update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order-delete'),
    path('order-articles/', OrderArticleListView.as_view(), name='orderarticle-list'),
    path('order-articles/new/', OrderArticleCreateView.as_view(), name='orderarticle-create'),
    path('order-articles/<int:pk>/', OrderArticleDetailView.as_view(), name='orderarticle-detail'),
    path('order-articles/<int:pk>/update/', OrderArticleUpdateView.as_view(), name='orderarticle-update'),
    path('order-articles/<int:pk>/delete/', OrderArticleDeleteView.as_view(), name='orderarticle-delete'),
]
    