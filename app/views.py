from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
import razorpay
from .models import Customer, Product, Cart, OrderPlaced, Category, Brand, Banner, Sale
from .forms import CustomerRegistrationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import MyPasswordChangeForm, CustomerProfileForm
from django.contrib.auth import views as auth_views

from django.db.models import Q

from django.views import View
from django.shortcuts import render
from django.db.models import Q
from .models import Product

class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = []

        # Only search if the query has at least 3 characters
        if len(query) >= 3:
            results = Product.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category_fk__name__icontains=query) |
                Q(brand_fk__name__icontains=query)
            ).distinct()

        context = {
            'query': query,
            'results': results,
            'min_length_required': len(query) < 3,  # So we can show a friendly message
        }
        return render(request, 'app/search_results.html', context)





def product_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(category_fk=category)
    brands = Brand.objects.filter(products__category_fk=category).distinct()
    context = {'category': category, 'products': products, 'brands': brands}
    return render(request, 'app/productlist.html', context)

def product_list_by_brand(request, category_slug, brand_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
    products = Product.objects.filter(category_fk=category, brand_fk=brand)
    brands = Brand.objects.filter(products__category_fk=category).distinct()
    context = {'category': category, 'products': products, 'brands': brands, 'selected_brand': brand}
    return render(request, 'app/productlist.html', context)

def product_list_by_price(request, category_slug, min_price, max_price):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(
        category_fk=category,
        discounted_price__gte=min_price,
        discounted_price__lte=max_price
    )
    brands = Brand.objects.filter(products__category_fk=category).distinct()
    context = {'category': category, 'products': products, 'brands': brands, 'price_range': f"₹{min_price} - ₹{max_price}"}
    return render(request, 'app/productlist.html', context)


class ProductView(View):
    def get(self, request):
        from django.utils import timezone

        # Only categories that actually have products
        categories = Category.objects.filter(products__isnull=False).distinct()

        # List of dictionaries: [{'category': cat, 'products': queryset}, ...]
        category_products_list = []
        for cat in categories:
            products = Product.objects.filter(category_fk=cat)
            category_products_list.append({
                'category': cat,
                'products': products
            })

        # Dynamic banners
        banners = Banner.objects.filter(is_active=True)

        # Active sales
        current_sales = Sale.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        context = {
            'banners': banners,
            'category_products_list': category_products_list,
            'current_sales': current_sales
        }
        return render(request, 'app/home.html', context) 

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        gallery_images = product.images.all()  # all additional images

        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(user=request.user, product=product).exists()

        context = {
            'product': product,
            'gallery_images': gallery_images,
            'item_already_in_cart': item_already_in_cart
        }
        return render(request, 'app/productdetail.html', context)


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')  
    product = Product.objects.get(id=product_id)

    # Prevent duplicate entry
    item_exist = Cart.objects.filter(user=user, product=product).exists()
    if not item_exist:
        Cart.objects.create(user=user, product=product)

    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        carts = Cart.objects.filter(user=user)

        # calculate amount
        amount = 0
        for item in carts:
            amount += item.quantity * item.product.discounted_price

        shipping = 70  # simple fixed shipping charge
        total_amount = amount + shipping if carts.exists() else 0

        context = {
            'carts': carts,
            'amount': round(amount, 2),
            'shipping': round(shipping, 2),
            'total_amount': round(total_amount, 2),
        }
        return render(request, 'app/addtocart.html', context)
    else:
        return redirect('login')



# ------------------ PLUS CART ------------------
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart_item = Cart.objects.get(product=prod_id, user=request.user)
        cart_item.quantity += 1
        cart_item.save()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 70.0 if amount > 0 else 0
        total_amount = amount + shipping
        cart_count = sum(p.quantity for p in cart)

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total_amount': total_amount,
            'cart_count': cart_count,
        }
        return JsonResponse(data)


# ------------------ MINUS CART ------------------
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        try:
            cart_item = Cart.objects.get(product=prod_id, user=request.user)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                quantity = cart_item.quantity
            else:
                cart_item.delete()
                quantity = 0  # means item removed completely
        except Cart.DoesNotExist:
            quantity = 0

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 70.0 if amount > 0 else 0
        total_amount = amount + shipping
        cart_count = sum(p.quantity for p in cart)

        data = {
            'quantity': quantity,
            'amount': amount,
            'total_amount': total_amount,
            'cart_count': cart_count,
        }
        return JsonResponse(data)


# ------------------ REMOVE CART ------------------
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        try:
            cart_item = Cart.objects.get(product=prod_id, user=request.user)
            cart_item.delete()
        except Cart.DoesNotExist:
            pass

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 70.0 if amount > 0 else 0
        total_amount = amount + shipping
        cart_count = sum(p.quantity for p in cart)

        data = {
            'amount': amount,
            'total_amount': total_amount,
            'cart_count': cart_count,
        }
        return JsonResponse(data)


def buy_now(request):
    return render(request, 'app/buynow.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, city = city,
                           state = state, zipcode = zipcode)
            reg.save()
            messages.success(request, 'Profile updates successfully !!')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    add = Customer.objects.filter(user = request.user)
    return render(request, 'app/address.html', {'add':add, 'active':'btn-primary'})


#Password Reset
class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = 'app/password_reset.html'
    email_template_name = 'app/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    # optional: you can customize form_class if needed

class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'app/password_reset_done.html'

class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'app/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'app/password_reset_complete.html'

#Password Change
class MyPasswordChangeView(PasswordChangeView):
    template_name = 'app/passwordchange.html'
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('home') 


def mobile(request, data=None, min_price=None, max_price=None):
    mobiles = Product.objects.filter(category='M')

    # if brand selected
    if data:
        mobiles = mobiles.filter(brand=data)

    # if price range selected
    if min_price and max_price:
        mobiles = mobiles.filter(discounted_price__gte=min_price, discounted_price__lte=max_price)

    context = {'mobiles': mobiles}
    return render(request, 'app/mobile.html', context)


def login(request):
    return render(request, 'app/login.html')

def custom_logout(request):
    logout(request)
    return redirect('home')


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})
    
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Congratulations !! Registered Successfully')
            
        return render(request, 'app/customerregistration.html', {'form':form})

@login_required
def checkout(request):
    if request.user.is_authenticated:
        user = request.user
        carts = Cart.objects.filter(user=user)
        customers = Customer.objects.filter(user=user)

    amount = 0
    for item in carts:
        amount+= item.quantity * item.product.discounted_price

    if carts:
        shipping = 70
    else:
        shipping = 0
  
    data = {
        'carts':carts,
        'amount':round(amount),
        'shipping':round(shipping),
        'total_amount':round(amount + shipping),
        'customers':customers
    }
        
    return render(request, 'app/checkout.html', data)

@login_required
def orders(request):
    user = request.user
    orders = OrderPlaced.objects.filter(user=user).order_by('-ordered_date')

    data = {
        'orders':orders
    }

    return render(request, 'app/orders.html', data)



def payment(request):
    user = request.user

    # If coming from checkout page (POST request)
    if request.method == "POST":
        selected_customer_id = request.POST.get("customer_id")
        if selected_customer_id:
            request.session["selected_customer_id"] = selected_customer_id
        else:
            messages.error(request, "Please select an address first.")
            return redirect("checkout")

    # Retrieve from session (so refresh doesn’t lose it)
    selected_customer_id = request.session.get("selected_customer_id")

    # Fetch the selected customer only
    selected_customer = None
    if selected_customer_id:
        selected_customer = Customer.objects.filter(id=selected_customer_id, user=user).first()

    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Compute totals
    amount = sum(c.quantity * c.product.discounted_price for c in cart_items)
    shipping = 70.0 if amount > 0 else 0
    total_amount = int((amount + shipping) * 100)  # in paise for Razorpay

    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": total_amount,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {"user_id": str(user.id)}
    }) if total_amount > 0 else {}

    context = {
        'selected_customer': selected_customer,
        'carts': cart_items,
        'amount': round(amount, 2),
        'shipping': round(shipping, 2),
        'total_amount_display': round(amount + shipping, 2),
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'app/payment.html', context)



def payment_done(request):
    user = request.user

    # 🟤 CASE A: COD
    if request.method == "POST" and request.POST.get('method') == 'cod':
        customer_id = request.POST.get("customer_id") or request.POST.get("selected_customer_id")
        if not customer_id:
            messages.error(request, "No address selected.")
            return redirect('payment')
        try:
            customer = Customer.objects.get(id=customer_id, user=user)
        except Customer.DoesNotExist:
            messages.error(request, "Invalid customer address.")
            return redirect('payment')

        cart_items = Cart.objects.filter(user=user)
        for c in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment_method='cod'
            )
        cart_items.delete()

        messages.success(request, "Order placed successfully (Cash On Delivery).")
        return redirect('orders')

    # 🟢 CASE B: Razorpay
    if request.method == 'POST' and request.POST.get('method') == 'razorpay':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        customer_id = request.POST.get('customer_id')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            payment_verified = True
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('payment')

        try:
            customer = Customer.objects.get(id=customer_id, user=user)
        except Customer.DoesNotExist:
            messages.error(request, "Invalid customer address.")
            return redirect('payment')

        cart_items = Cart.objects.filter(user=user)
        for c in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment_method='razorpay'
            )
        cart_items.delete()

        messages.success(request, "Payment successful and order placed.")
        return redirect('orders')

    # fallback
    return redirect('checkout')
