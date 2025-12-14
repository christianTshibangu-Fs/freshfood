from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, FormView, TemplateView, RedirectView
from .models import Product, Order, OrderArticle
# Create your views here.

def home(request):
    return render(request, 'food_app/home.html')

#### Product Views ###

class ProductCreateView(CreateView):
    model = Product
    fields = ['label', 'description', 'price', 'stock']
    template_name = 'food_app/product_form.html'
    success_url = '/products/'

# List view for all products
class ProductListView(ListView):
    model = Product
    ordering = ["label"]
    template_name = 'food_app/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

# Detail view for a single product
class ProductDetailView(DetailView):
    model = Product
    template_name = 'food_app/product_detail.html'
    context_object_name = 'product'

# Update view for editing a product
class ProductUpdateView(UpdateView):
    model = Product
    fields = ['label', 'description', 'price', 'stock']
    template_name_suffix = '_update_form'
    success_url = '/products/'

# Delete view for removing a product
class ProductDeleteView(DeleteView):
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
class OrderCreateView(CreateView):
    model = Order
    fields = ['customer']
    template_name = 'food_app/order_form.html'
    success_url = '/orders/'

# List view for all orders
class OrderedListView(ListView):
    model = Order
    ordering = ['-created_at']
    template_name = 'food_app/ordered_list.html'
    context_object_name = 'orders'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_articles'] = OrderArticle.objects.all()
        return context

# Detail view for a single order
class OrderDetailView(DetailView):
    model = Order
    template_name = 'food_app/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_articles'] = OrderArticle.objects.filter(order=self.object)
        return context
    
# Delete view for removing an order
class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'food_app/order_confirm_delete.html'
    success_url = '/orders/'    

# update view for editing an order
class OrderUpdateView(UpdateView):
    model = Order
    fields = ['customer']
    template_name_suffix = '_update_form'
    success_url = '/orders/'


### Order Article Views ###

# Create view for adding articles to an order
class OrderArticleCreateView(CreateView):
    model = OrderArticle
    fields = ['product', 'quantity', 'order']
    template_name = 'food_app/orderarticle_form.html'
    success_url = '/orders/'

class OrderArticleDeleteView(DeleteView):
    model = OrderArticle
    template_name = 'food_app/orderarticle_confirm_delete.html'
    success_url = '/orders/'

# Update view for editing an order article
class OrderArticleUpdateView(UpdateView):   
    model = OrderArticle
    fields = ['product', 'quantity', 'order']
    template_name_suffix = '_update_form'
    success_url = '/orders/'

# List view for all order articles
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
class OrderArticleDetailView(DetailView):
    model = OrderArticle
    template_name = 'food_app/orderarticle_detail.html'
    context_object_name = 'order_article'   