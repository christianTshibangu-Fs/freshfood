from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views 

urlpatterns = [

    # Vues d'authentification
    path('register/', views.register, name='register'), # Registration route
    path('login/', LoginView.as_view(template_name='food_app/login.html'), name='login'), # Login route
    path('logout/', LogoutView.as_view(template_name='food_app/logout.html'), name='logout'), # Logout route
    

    path('', views.index, name='index-app'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('products/', views.ProductListView.as_view(), name='product-list'), 
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('products/search/', views.ProductSearchView.as_view(), name='product-search'), 
    path('products/new/', views.ProductCreateView.as_view(), name='product-create'),

    path('orders/', views.OrderedListView.as_view(), name='order-list'),
    path('orders/new/', views.OrderView.as_view(), name='order-view'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order-update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order-delete'),
    path('orders/<int:pk>/user', views.UserOrderListView.as_view(), name='orders-user'),
    
    path('order-articles/', views.OrderArticleListView.as_view(), name='orderarticle-list'),
    path('order-articles/new/', views.OrderArticleCreateView.as_view(), name='orderarticle-create'),
    path('order-articles/<int:pk>/', views.OrderArticleDetailView.as_view(), name='orderarticle-detail'),
    path('order-articles/<int:pk>/update/', views.OrderArticleUpdateView.as_view(), name='orderarticle-update'),
    path('order-articles/<int:pk>/delete/', views.OrderArticleDeleteView.as_view(), name='orderarticle-delete'),
]
    