from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import logout, login, authenticate

def signup(request):
    return render(request, 'registration/signup.html')

def signup_action(request):
	if request.method == 'POST':
		_username = request.POST.get('username')

		new_user = User(
            username = _username,
        )
		new_user.set_password(request.POST.get('password1'))
		new_user.save()

		studata = Customer(
            user = User.objects.get(username=_username),
            name = request.POST.get('Name'),
            email = request.POST.get('email'),
        )
		studata.save()
	return redirect('login')

def _login(request):
    return render(request, 'registration/login.html')

def login_action(request):
	message = ''
	if request.method == 'POST':
		user = authenticate(
            username = request.POST.get('username'),
            password = request.POST.get('password'),
        )
		if user is not None:
			login(request, user)
			return redirect('store')
		else:
			message = 'Login failed!'
	return redirect('login')


def _logout(request):
	logout(request)
	return redirect('store')


def store(request):
	login = False
	if request.user.is_authenticated:
		login = True
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems, 'login':login}
	return render(request, 'store/store.html', context)


def cart(request):
	login = False
	if request.user.is_authenticated:
		login = True
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems, 'login':login}
	return render(request, 'store/cart.html', context)

def checkout(request):
	login = False
	if request.user.is_authenticated:
		login = True
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems, 'login':login}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)