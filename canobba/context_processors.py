from canobba.models import Coleccion

def active_class(request):
	path = request.path
	return {'path':path}

def colecciones(request):
	colecciones = Coleccion.objects.all().order_by("orden")
	return {'colecciones':colecciones}

def carrito_count(request):
	from carton.cart import Cart
	cart = Cart(request.session)
	if request.user.is_authenticated():
		cartw = request.user.wishlist.all()
	else:
		cartw = Cart(session=request.session, session_key='CART-wish')
	return { "cart":cart, "cartw":cartw }