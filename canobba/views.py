# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import *
from carton.cart import Cart
import json
from django.http import HttpResponse
from django.conf import settings
from carton.cart import Cart
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

SENDER_EMAIL = 'hola@canobba.com'
# RECEIVER = 'adda@canobba.com'
RECEIVER = 'carranzamario26@gmail.com'

def login_form(request):
	vars = {"title":"Login"}
	cartw = Cart(session=request.session, session_key='CART-wish')

	if request.method == "POST":
		email = request.POST.get("email")
		password = request.POST.get("pass")
		user = authenticate(username=email, password=password)
		if user:
			if user.is_active:
				login(request, user)
				#Se mueven todos los productos de la wishlist de sesion a la wishlist del usuario.
				for producto in cartw.items:
					#Ciclo para comprobar que no se agreguen repetidos.
					if user.wishlist.count() > 0:
						for w in user.wishlist.all():
							if producto.product.id != w.producto.id:
								wishl = WishlistDetalle()
								wishl.usuario = user
								wishl.producto = producto.product
								wishl.save()
								break
					else:
						wishl = WishlistDetalle()
						wishl.usuario = user
						wishl.producto = producto.product
						wishl.save()
				cartw.clear()

				messages.add_message(request, messages.INFO, 'Bienvenido(a) ' + user.usuario.nombre)
				if request.GET.get('car'):
					return redirect("show_cart")
				return redirect("home")
		messages.add_message(request, messages.ERROR, 'Usuario o contraseña son incorrectos')
	return render(request, 'login.html', vars)

@login_required
def logout_user(request):
	"""
	Sale de la sesion del usuario.
	"""
	logout(request)
	return redirect("home")

def registro(request):
	vars = {"title":"Registro"}
	if request.method == "POST":
		tipo = 0
		tipo = request.GET.get('tipo')
		nombre = request.POST.get("nombre")
		apellidos = request.POST.get("apellidos")
		email = request.POST.get("email")
		password = request.POST.get("pass")
		# try:
		user = User.objects.create(username=email, email=email)
		user.set_password(password)
		user.save()
		usuario = Usuario(user=user, email=email)
		# except:
			# messages.add_message(request, messages.ERROR, "El correo electrónico ingresado ya se encuentra registrado.")
			# return redirect("registro")
		try:
			if "cliente" == tipo:
				usuario.tipo = 1
				usuario.nombre = nombre
				usuario.apellidos = apellidos
			elif "artista" == tipo:
				usuario.tipo = 2
				usuario.nombre = nombre
				usuario.apellidos = apellidos
				usuario.biografia = request.POST.get('biografia')
				usuario.descripcion_trabajo = request.POST.get('descripcion')
				usuario.tecnicas = request.POST.get('tecnicas')
				profile_url = request.POST.get("profile_url")
				usuario.imagen = request.FILES.get("imagen")
				usuario.municipio = request.POST.get("u-ciudad")
				usuario.estado = request.POST.get("u-estado")
				usuario.profile_url = profile_url
			else:
				raise Exception(tipo)
			usuario.save()
			user = authenticate(username=email, password=password)
			# Problema empieza aqui
			if user is not None:
				# Enviar email de bienvenida con informacion de la cuenta
				if user.is_active:
					login(request, user)
					messages.add_message(request, messages.INFO, '¡Gracias por registrarte!.')
					from django.core.mail import EmailMultiAlternatives
					from django.template.loader import render_to_string
					from django.template import Context

					subject, from_email, to = 'Bienvenido a Canobba','Registro Canobba <'+ SENDER_EMAIL+'>', email
					context = "<p style='color:#434343'>Bienvenido<br>"
					context += "Gracias por registrarse.<br>"
					context += "<h5 align='center'>Datos de acceso al sitio</h5><br>"
					context += "<b>Correo:</b> " + email + "<br>"
					context += u"<b>Contraseña:</b> " + password + "<br>"
					context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
					context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
					context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
					html_content = render_to_string('email_info.html', {'asunto':"Hola %s, gracias por registrarse con nosotros!" % usuario.nombre,
																'context': context})
					msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
					msg.attach_alternative(html_content, "text/html")
					msg.send()
					if request.GET.get('car'):
						return redirect("show_cart")
					return redirect("home")
		except Exception as detail:
			print detail
			#'El correo electrónico ingresado ya existe.'
			messages.add_message(request, messages.ERROR, detail)
			return redirect("registro")
	return render(request, 'log_registro.html', vars)

def recover_pass(request):
	"""
	Cambia la contraseña del usuario.
	"""
	title = "Cambiar contraseña"
	if request.method == "POST":
		user = request.user
		passw = request.POST.get('pass')
		apass = request.POST.get('apass')
		if user.check_password(apass):
			user.set_password(passw)
			user.save()
			usuario = authenticate(email=user.email, password=passw)
			login(request, usuario)
			messages.add_message(request, messages.INFO, u'Se cambió la contraseña correctamente.')
			return redirect("home")
		messages.add_message(request, messages.ERROR, u'La contraseña anterior ingresada no es correcta.')
	vars = {
		"title":title,
	}
	return render(request, "recover_pass.html", vars)

def reset_pass(request):
	"""
	Asigna una nueva contraseña al usuario y la envia al correo.
	"""
	if request.method == "POST":
		email = request.POST.get("email")
		import string
		import random
		try:
			usuario = Usuario.objects.get(email=email)
			new_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
			usuario.set_password(new_pass)
			usuario.save()
			from django.core.mail import EmailMultiAlternatives
			from django.template.loader import render_to_string
			from django.template import Context

			subject, from_email, to = u'Recuperar Contraseña Canobba', SENDER_EMAIL, email
			context = u"<p style='color:#434343'>Recuperar Contraseña<br>"
			context += u"Su nueva contraseña para el acceso a Canobba es:.<br>"
			context += u"->: " + new_pass + "<br>"
			context += u"Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
			context += u"No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
			context += u"<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
			html_content = render_to_string('email_info.html', {'context': context})
			msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
			msg.attach_alternative(html_content, "text/html")
			msg.send()

			messages.add_message(request, messages.SUCCESS, u'Se envió un correo con la nueva contraseña a %s' % email)
		except Exception as detail:
			print detail
			messages.add_message(request, messages.ERROR, u'El correo ingresado no se encuentra registrado.')

	vars = {
		"title":"Recuperar Contraseña",
	}

	return render(request, "reset_pass.html", vars)

def home(request):
	'''
	Rendera la pantalla principal del sitio web
	'''
	disenos = Producto.objects.all().order_by("-id")[0:15]
	filas = FilaInicio.objects.all().order_by("-id")
	vars = {"title":"Bienvenidos", "disenos":disenos, "slider":get_slider(), "filas":filas}
	return render(request, "index.html", vars)

def colecciones(request):
	'''
	Rendera la pantalla de colecciones
	'''
	vars = {"title":"Colecciones", "slider":get_slider()}
	return render(request, "colecciones.html", vars)

def materiales(request):
	'''
	Rendera la pantalla de materiales
	'''
	vars = {"title":"Materiales"}
	return render(request, "materiales.html", vars)

def coleccion(request, col_slug):
	'''
	Modificar!
	Muestra los diseños que corresponden a la coleccion seleccionada
	'''
	try:
		slider = Slider.objects.all()[0]
	except:
		slider = False

	coleccion = Coleccion.objects.get(slug=col_slug)
	#disenos = Producto.objects.filter(coleccion=coleccion).order_by("id")
	disenos = coleccion.disenos.filter(diseno__eliminado=False, diseno__aprobado=True)
	title = "Coleccion " + coleccion.nombre
	vars = {"title":title, "coleccion":coleccion, "disenos":disenos, "slider":get_slider()}
	return render(request, "select_coleccion.html", vars)

def diseno(request, diseno_slug):
	'''
	Muestra el diseño a detalle
	'''
	diseno = Producto.objects.get(slug=diseno_slug)
	title = diseno.nombre
	materiales = Material.objects.all().order_by("material").exclude(material=1).exclude(material=2)
	has_medidas = diseno.imagenes.all()
	medidas = diseno.imagenes.filter(horizontal=False).order_by("medida")
	vars = {"title":title, "diseno":diseno, "materiales":materiales, "medidas":medidas, "has_medidas":has_medidas}
	return render(request, "diseno.html", vars)

def contacto(request):
	vars = {"title":"Contacto"}
	if request.method == "POST":
		from django.core.mail import EmailMultiAlternatives
		from django.template.loader import render_to_string
		from django.template import Context

		subject, from_email, to = 'Nuevo contacto Canobba', 'Contacto Canobba <'+ SENDER_EMAIL+'>', RECEIVER
		context = "<p style='color:#434343'>Contacto<br>"
		context += "informacion del contacto:.<br>"
		context += u"Nombre: " + request.POST.get('nombre') + "<br>"
		context += u"Email: " + request.POST.get('email') + "<br>"
		context += u"Mensaje: " + request.POST.get('mensaje') + "<br>"
		html_content = render_to_string('email_info.html', {'context': context})
		msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		messages.add_message(request, messages.SUCCESS, u'Su mensaje ha sido enviado correctamente, en breve nos comunicaremos con usted.')
	return render(request, "contacto.html", vars)

def buscar(request):
	'''
	Busca diseños por tags y nombre
	'''
	from django.db.models import Q
	try:
		slider = Slider.objects.all()[0]
	except:
		slider = False
	q = request.GET.get("q")
	title = "Buscar " + q
	disenos = Producto.objects.filter( Q(tags__name__in=[q]) | Q(nombre__icontains=q) ).distinct()
	vars = { "title":title, "disenos":disenos, "es_busqueda":True, "slider":get_slider() }
	return render(request, "select_coleccion.html", vars)

def get_buscador(request):
	'''
		Nuevo buscador autocomplete , ahora busca por diseños / artistas
	'''
	if request.is_ajax():
		import json
		from django.db.models import Q
		q = request.GET.get('q')
		disenos = Producto.objects.filter( Q(tags__name__in=[q]) | Q(nombre__icontains=q) ).distinct()
		profile = Usuario.objects.filter( Q(nombre__icontains=q) | Q(apellidos__icontains=q) | Q(tipo__iexact='Diseñador') ).distinct()
		results = []
		designs = {'text': 'Diseños', 'children': []}
		for d in disenos:
			d_json = {}
			d_json['id'] = d.pk
			d_json['text'] = d.nombre
			d_json['type'] = '1'
			d_json['slug'] = d.slug
			designs['children'].append(d_json)


		artist = {'text': 'Artistas', 'children': []}
		for a in profile:
			a_json = {}
			a_json['id'] = a.pk
			a_json['text'] = a.nombre + ' ' + a.apellidos
			a_json['type'] = '2'
			a_json['profile_url'] = a.profile_url
			a_json['imagen'] = str(a.imagen.url) if a.imagen else None
			artist['children'].append(a_json)
		if designs['children']:
			results.append(designs)
		if artist['children']:
			results.append(artist)
        data = json.dumps(results)
	return HttpResponse(data,mimetype="application/json")


def get_material_ajax(request):
	'''
	** AJAX **
	Se utiliza para cambiar el precio del diseño por ajax solamente
	'''
	from django.core import serializers
	id = request.GET.get("pk")
	material = Material.objects.filter(id=id)
	f = ("material", "precio1", "precio2", "precio3", "precio4", "precio5", "precio6", "precio7", "precio8")
	data = serializers.serialize('json', material, fields=f)
	return HttpResponse(data, mimetype="application/json")

def check_profile_ajax(request):
	"""
	** AJAX **
	Se utiliza para comprobar si el profile url ingresado en el registro no esta siendo usado por otro usuario.
	"""
	from django.core import serializers
	s = request.GET.get("s")
	result = "False"
	try:
		u = Usuario.objects.get(profile_url=s)
		result = "True"
	except:
		result = "False"

	result = {"message":result}
	import json
	return HttpResponse(json.dumps(result), mimetype="application/json")

def add_session_cart(request):
	'''
	Agrega diseños al carrito de la sesion
	'''
	req = request.GET.get
	cart = Cart(request.session)
	cartw = Cart(session=request.session, session_key='CART-wish')

	product = Producto.objects.get(id=req('pk'))

	if req("inc"):
		cart.set_quantity(int(req("inc")))
		return redirect("show_cart")

	producto_carrito = ProductoCarrito()
	#producto_carrito.producto = product
	material = Material.objects.get(id=req('mt'))
	precio = 0
	medida = ''

	if req("sz") == "1":
		precio = material.precio1
		medida = '50cm x 60cm'
	elif req("sz") == "2":
		precio = material.precio2
		medida = '60cm x 90cm'
	elif req("sz") == "3":
		precio = material.precio3
		medida = '70cm x 70cm'
	elif req("sz") == "4":
		precio = material.precio4
		medida = '80cm x 120cm'
	elif req("sz") == "5":
		precio = material.precio5
		medida = '100cm x 100cm'
	elif req("sz") == "6":
		precio = material.precio6
		medida = '100cm x 150cm'
	elif req("sz") == "7":
		precio = material.precio7
		medida = '115cm x 180cm'
	elif req("sz") == "8":
		precio = material.precio8
		medida = '200cm x 120cm'

	orientacion = req("hor")
	try:
		producto_carrito = ProductoCarrito.objects.get(producto=product, medida=medida, material=material, orientacion=orientacion)
	except Exception as detail:
		print detail
		producto_carrito.producto = product
		producto_carrito.medida = medida
		producto_carrito.material = material
		producto_carrito.orientacion = orientacion
		producto_carrito.precio = precio
		producto_carrito.save()

	if req('wish') == "1":
		if request.user.is_authenticated():
			for w in request.user.wishlist.all():
				if w.producto.id == producto_carrito.id:
					messages.add_message(request, messages.ERROR, u'El producto ya se encuentra en sus favoritos.')
					return redirect("diseno", product.slug)
			wishl = WishlistDetalle()
			wishl.usuario = request.user
			wishl.producto = producto_carrito
			wishl.save()
			messages.add_message(request, messages.SUCCESS, u'Se agregó correctamente el diseño %s a sus favoritos' % (producto_carrito.producto.nombre))
		else:
			if not cartw.__contains__(producto_carrito):
				cartw.add(producto_carrito, price=producto_carrito.precio)
				messages.add_message(request, messages.SUCCESS, u'Se agregó correctamente el diseño %s a sus favoritos' % (producto_carrito.producto.nombre))
			else:
				messages.add_message(request, messages.ERROR, u'El producto ya se encuentra en sus favoritos.')
	else:
		cart.add(producto_carrito, price=producto_carrito.precio)
		messages.add_message(request, messages.SUCCESS, u'Se agregó correctamente el diseño %s al carrito' % (producto_carrito.producto.nombre))

	if req('car') == "1":
		return redirect("show_cart")
	elif req('car') == "0":
		return redirect("colecciones")

	return redirect("diseno", product.slug)

def show_cart(request):
	'''
	Muestra el carrito de sesion asdfdf
	'''
	carrito = Cart(request.session)
	subtotal = 0
	total = 0
	for producto in carrito.items:
		total += producto.subtotal

	subtotal = float(total) / float(1.16)
	iva = subtotal * float(0.16)
	total = subtotal + iva
	vars = {
		"title":"Mi carrito",
		"cart" : carrito,
		"subtotal":subtotal,
		"iva":iva,
		"total":total,
	}
	return render(request, "carrito.html", vars)

def remove_session_cart(request, id):
	'''
	Elimina diseños del carrito
	'''
	cart = Cart(request.session)
	product = ProductoCarrito.objects.get(id=id)
	cart.remove(product)
	#product.delete()
	messages.add_message(request, messages.INFO, u'Se eliminó el diseño %s del carrito' % (product.producto.nombre))
	return redirect("show_cart")

def set_qty_cart(request):
	cart = Cart(request.session)
	product = ProductoCarrito.objects.get(id=request.GET.get('pk'))
	cart.set_quantity(product, int(request.GET.get('qty')))
	messages.add_message(request, messages.INFO, u'Su carrito se modificó correctamente')
	return redirect("show_cart")


def guardar_datos_envio(request):
	if request.is_ajax():
		r = request.POST.get
		carrito = Cart(request.session)

		pedido = Pedido()
		pedido_detalle = PedidoDetalle()

		pedido.subtotal = r("subtotal")
		pedido.total = carrito.total
		pedido.save()

		for producto in carrito.items:
			pedido_detalle.pedido = pedido
			pedido_detalle.producto = producto.product
			pedido_detalle.cantidad = producto.quantity
			pedido_detalle.save()


		vars = {
			"title":"Mi carrito",
			"cart" : carrito,
			"subtotal":pedido.subtotal,
			"pedido":pedido
		}
		return render(request, "carrito.html", vars)

def generar_pedido(request):
	'''
	Crea el pedido a partir del carrito de compras.
	'''
	r = request.POST.get
	carrito = Cart(request.session)
	logged = request.user.is_authenticated()
	pedido = Pedido()

	pedido.pedido = pedido
	if logged:
		pedido.usuario = request.user
	pedido.nombre = r("nombre")
	pedido.apellidos = r("apellidos")
	pedido.direccion = r("direccion")
	pedido.ciudad = r("ciudad")
	pedido.estado = r("estado")
	pedido.codigo_postal = r("codigo_p")
	pedido.telefono = r("telefono")
	pedido.email = r("email")
	pedido.no_exterior = r("numero")
	#24/03/15
	pedido.no_interior = r("no_interior")
	pedido.colonia = r("colonia")

	pedido.save()

	for producto in carrito.items:
		pedido_detalle = PedidoDetalle()
		pedido_detalle.pedido = pedido
		pedido_detalle.producto = producto.product
		pedido_detalle.cantidad = producto.quantity
		pedido_detalle.save()

	carrito.clear()
	# Envio de correo al cliente
	from django.core.mail import EmailMultiAlternatives
	from django.template.loader import render_to_string
	from django.template import Context

	datos = {
		"pedido":pedido,
	}

	html_content = render_to_string('email_pedido.html', datos)
	if logged:
		subject, from_email, to = 'Nuevo pedido', 'Pedidos Canobba <'+ SENDER_EMAIL+'>', request.user.email
	else:
		subject, from_email, to = 'Nuevo pedido', 'Pedidos Canobba <'+ SENDER_EMAIL+'>', pedido.email
	msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
	msg.attach_alternative(html_content, "text/html")
	msg.send()
	#Admin
	datos = {
		"pedido":pedido,
		"admin":True,
	}

	html_content = render_to_string('email_pedido.html', datos)
	subject, from_email = 'Nuevo pedido', 'Pedidos Canobba <'+ SENDER_EMAIL+'>'
	msg = EmailMultiAlternatives(subject, html_content, from_email, [RECEIVER,])
	msg.attach_alternative(html_content, "text/html")
	msg.send()

	messages.add_message(request, messages.INFO, "Su pedido se generó correctamente.")
	return redirect("detalle_pedido", str(pedido.id))

def get_slider():
	'''
	Método para traer el slider principal
	'''
	slider = ""
	try:
		slider = Slider.objects.all()[0]
	except:
		slider = False

	return slider

def blog(request):
	'''
	Eliminar despues de usar la app blog
	'''
	return render(request, "blog/base.html")


def detalle_pedido(request, id):
	'''
	Muestra el detalle del pedido.
	'''
	title = "Detalles de Pedido"
	try:
		pedido = Pedido.objects.get(id=id)
		producto_dic = []
		if pedido.usuario:
			pedido = Pedido.objects.get(id=id, usuario=request.user)
		pedido_detalle = PedidoDetalle.objects.filter(pedido=pedido.pk)
		for producto in pedido_detalle:
			p_info = {}
			p_info['name'] = producto.producto.producto.nombre
			p_info['description'] = producto.producto.producto.descripcion
			p_info['unit_price'] = str(producto.producto.precio)
			p_info['quantity'] = producto.cantidad
			p_info['sku'] = ''
			p_info['category'] = ''
			producto_dic.append(p_info)

		if request.method == "POST":
			import conekta
			conekta.api_version = "1.0.0"
			conekta.api_key = "key_LrRrcE7WaJCRuWKFggUk3g"
			#conekta.api_key = "key_va44GRJ7aZN3Gxa25vqcBA"
			conekta.locale = 'es'
			try:
				charge = conekta.Charge.create({
					"amount": int(pedido.get_total()*100),
					#"amount": int(3 * 100),
					"currency": "MXN",
					"description": "Pago a Canobba Fotolienzo, folio# " + str(pedido.folio),
					"reference_id": str(pedido.folio),
					"card": request.POST.get('conektaTokenId'), #request.form["conektaTokenId"], request.params["conektaTokenId"], "tok_a4Ff0dD2xYZZq82d9"
					"details":{
						"name":pedido.nombre + " " + pedido.apellidos,
						"phone":pedido.telefono,
						"email":pedido.email,
						"line_items":producto_dic,
						"shipment": {
							"carrier":"tinypack",
							"service":"nacional",
							"price": 0,
							"address": {
								"street1": pedido.direccion,
								"city":pedido.ciudad,
								"state":pedido.estado,
								"zip":pedido.codigo_postal,
								"country":"Mexico"
							}
						}
					}
				})

				messages.add_message(request, messages.SUCCESS, "Pago registrado correctamente.")
				pedido.forma_pago = "Conekta"
				pedido.status = 1
				pedido.save()
				from django.core.mail import EmailMultiAlternatives
				from django.template.loader import render_to_string
				from django.template import Context

				if pedido.usuario:
					subject, from_email, to = 'Pago registrado en Canobba', 'Pagos Canobba <'+ SENDER_EMAIL+'>', request.user.email
				else:
					subject, from_email, to = 'Pago registrado en Canobba', 'Pagos Canobba <'+ SENDER_EMAIL+'>', pedido.email
				context = "<p style='color:#434343'>Se registró un pago en Conekta del pedido con folio: "+str(pedido.folio)+"<br>"
				context += "Monto: " + str(pedido.get_total()) + " MXN.<br>"
				context += "<a href='http://canobba.com/detalle_pedido/"+str(pedido.id)+"/'>Ver pedido</a><br>"
				context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
				context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
				context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
				html_content = render_to_string('email_info.html', {'context': context})
				msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
				msg.attach_alternative(html_content, "text/html")
				msg.send()
				#Admin
				context = "<p style='color:#434343'>Se registró un pago en Conekta del pedido con folio: "+str(pedido.folio)+"<br>"
				context += "Monto: $" + str(pedido.get_total()) + " MXN.<br>"
				context += "<a href='http://canobba.com/admin/canobba/pedido/"+str(pedido.id)+"/'>Ver pedido</a><br>"
				context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
				context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
				context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
				html_content = render_to_string('email_info.html', {'context': context})
				msg = EmailMultiAlternatives(subject, html_content, from_email, [RECEIVER,])
				msg.attach_alternative(html_content, "text/html")
				msg.send()
				return redirect("detalle_pedido", str(pedido.id))

			except conekta.ConektaError as e:
				print e[0]
				messages.add_message(request, messages.ERROR, e[0]['message'])
	except:
		messages.add_message(request, messages.ERROR, 'El pedido no existe.')
		return redirect("home")

	vars = {
		"title":title,
		"pedido":pedido,
	}

	return render(request, "detalle_pedido.html", vars)

@login_required
def mis_pedidos(request):
	"""
	Muestra los pedidos del usuario logueado.
	"""
	pedidos = Pedido.objects.filter(usuario=request.user)

	vars = {
		"pedidos":pedidos,
		"title":"Mis Pedidos",
	}

	return render(request, "mis_pedidos.html", vars)

def paypal_return(request, id):
	"""
	Pantalla de regreso de paypal.
	"""
	try:
		pedido = Pedido.objects.get(id=id)
		pedido.forma_pago = "Paypal"
		pedido.status = 1
		pedido.save()
		from django.core.mail import EmailMultiAlternatives
		from django.template.loader import render_to_string
		from django.template import Context

		if pedido.usuario:
			subject, from_email, to = 'Pago registrado en Canobba', 'Pagos Canobba <'+ SENDER_EMAIL+'>', request.user.email
		else:
			subject, from_email, to = 'Pago registrado en Canobba', 'Pagos Canobba <'+ SENDER_EMAIL+'>', pedido.email
		context = "<p style='color:#434343'>Se registró un pago en Paypal del pedido con folio: "+str(pedido.folio)+"<br>"
		context += "Monto: $" + str(pedido.get_total()) + " MXN.<br>"
		context += "<a href='http://canobba.com/detalle_pedido/"+str(pedido.id)+"/'>Ver pedido</a><br>"
		context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
		context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
		context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
		html_content = render_to_string('email_info.html', {'context': context})
		msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		#Admin
		context = "<p style='color:#434343'>Se registró un pago en Paypal del pedido con folio: "+str(pedido.folio)+"<br>"
		context += "Monto: $" + str(pedido.get_total()) + " MXN.<br>"
		context += "<a href='http://canobba.com/admin/canobba/pedido/"+str(pedido.id)+"/'>Ver pedido</a><br>"
		context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
		context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
		context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
		html_content = render_to_string('email_info.html', {'context': context})
		msg = EmailMultiAlternatives(subject, html_content, from_email, [RECEIVER,])
		msg.attach_alternative(html_content, "text/html")
		msg.send()

		messages.add_message(request, messages.SUCCESS, "Pago registrado correctamente.")
		return redirect("detalle_pedido", str(pedido.id))
	except:
		messages.add_message(request, messages.ERROR, "El pedido no existe.")
		return redirect("home")

def deposito(request, id):
	"""
	Muestra la pantalla con los datos de depósito bancario.
	"""
	try:
		pedido = Pedido.objects.get(id=id)
		vars = {
			"pedido":pedido,
			"title":"Depósito",
		}

		return render(request, "deposito.html", vars)
	except Exception as detail:
		print detail
		messages.add_message(request, messages.ERROR, "El pedido no existe.")
		return redirect("home")

def remove_wishlist(request, id):
	"""
	Elimina productos de la wishlist.
	"""
	producto = ProductoCarrito.objects.get(id=id)
	cartw = Cart(session=request.session, session_key='CART-wish')
	if request.user.is_authenticated():
		for w in request.user.wishlist.all():
			if producto.id == w.producto.id:
				w.delete()
	else:
		cartw.remove(producto)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def move_cart(request, id):
	"""
	Mueve un producto de la wishlist al carrito.
	"""
	cart = Cart(request.session)
	cartw = Cart(session=request.session, session_key='CART-wish')
	producto = ProductoCarrito.objects.get(id=id)
	cart.add(producto, price=producto.precio)

	if not request.user.is_authenticated():
		cartw.remove(producto)
	else:
		for w in request.user.wishlist.all():
			if producto.id == w.producto.id:
				w.delete()
	messages.add_message(request, messages.SUCCESS, u"Se agregó correctamente el diseño %s al carrito" % producto.producto.nombre)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def get_orientacion(request):
	"""
	AJAX
	Obitene las medidas del diseño por la orientacion seleccionada.
	"""
	from django.core import serializers

	orientacion = request.GET.get("or")
	id = request.GET.get("pk")
	diseno = Producto.objects.get(id=id)

	# verifica que se cree un bucle infinito si no tiene ninguno de los 2
	has_medidas = diseno.imagenes.all()

	if has_medidas:
		if orientacion == "horizontal":
			medidas = diseno.imagenes.filter(horizontal=True).order_by("medida")
		else:
			medidas = diseno.imagenes.filter(horizontal=False).order_by("medida")
	else:
		data = [{'message':'El diseño no cuenta con medidas disponibles', 'status':'error'}]
		return HttpResponse(json.dumps(data), mimetype="application/json")

	lista = []
	for med in medidas:
		dic = {"imagen":med.imagen.url, "medida":str(med.medida), "disp":str(med.get_medida_display())}
		lista.append(dic)

	data = json.dumps(lista)
	return HttpResponse(data, mimetype="application/json")

def ver_perfil(request, profile):
	"""
	Muestra el perfil del diseñador.
	"""
	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	try:
		user = User.objects.get(id=profile)
		disenador = user.usuario
		dis = disenador.disenos.all()
		wish = WishlistDetalle.objects.filter(usuario__profile_url=profile)

		page = request.GET.get('page')
		paginator = Paginator(dis, 8)
		try:
			disenos = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			disenos = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			disenos = paginator.page(paginator.num_pages)

		vars = {
			"title":"Perfil de " + disenador.nombre,
			"disenador":disenador,
			"disenos":disenos,
			"favoritos":len(wish),
			"count_disenos":len(disenador.disenos.all())
		}

		if request.user == disenador:
			if request.GET.get("pub") == "1":
				return render(request, "perfil.html", vars)
			return render(request, "perfil_admin.html", vars)
		else:
			return render(request, "perfil.html", vars)

		return render(request, "perfil.html", vars)
	except Exception as detail:
		raise Exception(profile)
		# messages.add_message(request, messages.ERROR, u"El diseñador no existe. " + str(detail))
		return redirect("home")

def ver_favoritos(request, profile):
	'''
		Muestra los favoritos del diseñador
	'''
	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	try:
		disenador = Usuario.objects.get(profile_url=profile)
		wish = WishlistDetalle.objects.filter(usuario__profile_url=profile)

		vars = {
			"title":"Favoritos de " + disenador.nombre,
			"disenador":disenador,
			"favoritos":len(wish),
		}
		if request.user == disenador:
			if request.GET.get('pub') == '1':
				return render(request,'public_favoritos.html',vars)
		return render(request, "public_favoritos.html", vars)
	except Exception as detail:
		messages.add_message(request, messages.ERROR, u"El diseñador no existe. ")
		return redirect("login_form")


def votar(request, profile, voto):
	"""
	Genera y almacena una nueva calificación.
	"""
	try:
		disenador = Usuario.objects.get(profile_url=profile)
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, u"Ingresar al sistema para poder calificar a un diseñador.")
			return redirect("ver_perfil", disenador.profile_url)
		if disenador != request.user:
			try:
				uvoto = Rating.objects.get(disenador=disenador, usuario=request.user)
				messages.add_message(request, messages.INFO, u"Ya calificaste a %s" % (disenador.nombre))
				return redirect("ver_perfil", disenador.profile_url)
			except:
				r = int(voto)
				rating = Rating()
				rating.rating = r
				rating.disenador = disenador
				rating.usuario = request.user
				rating.save()
				messages.add_message(request, messages.SUCCESS, u"Calificación enviada.")
		else:
			messages.add_message(request, messages.ERROR, u"No te puedes calificar a ti mismo ;).")
		return redirect("ver_perfil", disenador.profile_url)
	except Exception as detail:
		messages.add_message(request, messages.ERROR, u"El diseñador no existe. " + str(detail))
		return redirect("home")

def follow(request, profile):
	"""
	Funcion para seguir a un diseñador.
	"""
	try:
		disenador = Usuario.objects.get(profile_url=profile)
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, u"Ingresar al sistema para poder seguir a un diseñador.")
			return redirect("ver_perfil", disenador.profile_url)
		if disenador != request.user:
			try:
				follower = Follower.objects.get(disenador=disenador, usuario=request.user)
				messages.add_message(request, messages.INFO, u"Ya estas siguiendo a %s" % (disenador.nombre))
				return redirect("ver_perfil", disenador.profile_url)
			except:
				follow = Follower()
				follow.disenador = disenador
				follow.usuario = request.user
				follow.save()
				messages.add_message(request, messages.SUCCESS, u"Siguiendo a %s" % (disenador.nombre))
		else:
			messages.add_message(request, messages.ERROR, u"No puedes seguirte a ti mismo ;P.")
		return redirect("ver_perfil", disenador.profile_url)
	except Exception as detail:
		messages.add_message(request, messages.ERROR, u"El diseñador no existe. " + str(detail))
		return redirect("home")

def actualizar(request, profile):
	"""
	Actualiza los datos del perfil de un diseñador.
	"""
	if request.method == "POST":
		disenador = Usuario.objects.get(profile_url=profile)
		disenador.nombre = request.POST.get("nombre")
		disenador.apellidos = request.POST.get("apellidos")
		disenador.municipio = request.POST.get("municipio")
		disenador.estado = request.POST.get("estado")
		disenador.biografia = request.POST.get("biografia")
		if request.FILES.get("imagen"):
			disenador.imagen = request.FILES.get("imagen")
		disenador.save()
		messages.add_message(request, messages.SUCCESS, u"Datos actualizados correctamente.")
		return redirect("ver_perfil", disenador.profile_url)

	return redirect("home")

def following(request, profile):
	"""
	Muestra los diseñadores a los que éste diseñador sigue.
	"""
	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	try:
		disenador = Usuario.objects.get(profile_url=profile)
		sigs = disenador.siguiendo.all()

		page = request.GET.get('page')
		paginator = Paginator(sigs, 8)
		try:
			siguiendo = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			siguiendo = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			siguiendo = paginator.page(paginator.num_pages)

		vars = {
			"title":"Following",
			"disenador":disenador,
			"siguiendo":siguiendo,
		}

		return render(request, "following.html", vars)
	except Exception as detail:
		messages.add_message(request, messages.ERROR, U"El diseñador no existe. " + str(detail))
		return redirect("home")

def followers(request, profile):
	"""
	Muestra los seguidores de éste diseñador.
	"""
	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	try:
		disenador = Usuario.objects.get(profile_url=profile)
		follows = disenador.followers.all()

		page = request.GET.get('page')
		paginator = Paginator(follows, 8)
		try:
			followers = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			followers = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			followers = paginator.page(paginator.num_pages)

		vars = {
			"title":"Followers",
			"disenador":disenador,
			"followers":followers,
		}

		return render(request, "followers.html", vars)
	except Exception as detail:
		messages.add_message(request, messages.ERROR, U"El diseñador no existe. " + str(detail))
		return redirect("home")

def show_pdf(request):
	"""
	Aviso de privacidad.
	"""
	with open(settings.STATIC_ROOT + 'aviso.pdf', 'r') as pdf:
		response = HttpResponse(pdf.read(),content_type='application/pdf')
		response['Content-Disposition'] = 'filename=aviso.pdf'
		return response
	pdf.closed

def subir_diseno(request, profile, dis=None):
	"""
	Sube un diseño.
	"""
	import os
	from django.core.files.storage import default_storage
	from django.core.files.base import ContentFile
	from filebrowser.base import FileObject

	colecciones = Coleccion.objects.all()
	# TODO: Error is here
	try:
		disenador = Usuario.objects.get(profile_url=profile)
		if request.user != disenador:
			messages.add_message(request, messages.ERROR, U"Ingresar al sistema para subir un diseño.")
			return redirect("home")
	except:
		messages.add_message(request, messages.ERROR, U"El diseñador no existe.")
		return redirect("home")

	if dis:
		try:
			diseno = Producto.objects.get(id=dis)
		except:
			messages.add_message(request, messages.ERROR, U"El diseño no existe.")
			return redirect("home")
	else:
		diseno = Producto()

	if request.method == "POST":
		req_imgs = request.FILES.get
		req = request.POST.get
		diseno.usuario = disenador
		diseno.nombre = req("nombre")
		diseno.descripcion = req("descripcion")
		#Tags
		if diseno.id:
			diseno.tags.clear()
			if req("etiqueta"):
				tags = req("etiqueta").strip(" ").split(",")
				for tag in tags:
					diseno.tags.add(tag)
		#Imagen principal
		if req_imgs("img_principal"):
			if diseno.id:
				diseno.imagen.delete()
				diseno.imagen.delete_versions()
				diseno.imagen.delete_admin_versions()
			data = req_imgs("img_principal")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			diseno.imagen = FileObject(path)
		#Imagen principal horizontal
		if req_imgs("img_principal_h"):
			if diseno.id:
				diseno.img_horizontal.delete()
				diseno.img_horizontal.delete_versions()
				diseno.img_horizontal.delete_admin_versions()
			data = req_imgs("img_principal_h")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			diseno.img_horizontal = FileObject(path)
		#Imagen principal vertical
		if req_imgs("img_principal_v"):
			if diseno.id:
				diseno.img_vertical.delete()
				diseno.img_vertical.delete_versions()
				diseno.img_vertical.delete_admin_versions()
			data = req_imgs("img_principal_v")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			diseno.img_vertical = FileObject(path)
		sel_colecciones = request.POST.getlist("coleccion")
		diseno.save()
		#Se agregan las colecciones a las que pertenece este diseño
		if sel_colecciones:
			for coleccion in diseno.categorias.all():
				coleccion.delete()

			for coleccion in sel_colecciones:
				col = ColeccionExtra()
				col.diseno = diseno
				col.coleccion = Coleccion.objects.get(id=coleccion)
				col.save()

		#Medidas horizontales disponibles
		if req_imgs("img_principal_200x120"):
			try:
				med = ImagenProducto.objects.get(medida=8, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 8
			med.producto = diseno
			data = req_imgs("img_principal_200x120")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = True
			med.save()
		if req_imgs("img_principal_100x100"):
			try:
				med = ImagenProducto.objects.get(medida=5, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 5
			med.producto = diseno
			data = req_imgs("img_principal_100x100")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = True
			med.save()
		if req_imgs("img_principal_70x70"):
			try:
				med = ImagenProducto.objects.get(medida=3, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 3
			med.producto = diseno
			data = req_imgs("img_principal_70x70")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = True
			med.save()
		#Medidas verticales disponibles
		if req_imgs("img_principal_115x180"):
			try:
				med = ImagenProducto.objects.get(medida=7, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 7
			med.producto = diseno
			data = req_imgs("img_principal_115x180")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = False
			med.save()
		if req_imgs("img_principal_100x150"):
			try:
				med = ImagenProducto.objects.get(medida=6, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 6
			med.producto = diseno
			data = req_imgs("img_principal_100x150")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = False
			med.save()
		if req_imgs("img_principal_80x120"):
			try:
				med = ImagenProducto.objects.get(medida=4, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 4
			med.producto = diseno
			data = req_imgs("img_principal_80x120")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = False
			med.save()
		if req_imgs("img_principal_60x90"):
			try:
				med = ImagenProducto.objects.get(medida=2, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 2
			med.producto = diseno
			data = req_imgs("img_principal_60x90")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = False
			med.save()
		if req_imgs("img_principal_50x60"):
			try:
				med = ImagenProducto.objects.get(medida=1, producto=diseno)
				med.imagen.delete()
				med.imagen.delete_versions()
				med.imagen.delete_admin_versions()
				med.delete()
			except Exception as detail:
				print detail
			med = ImagenProducto()
			med.medida = 1
			med.producto = diseno
			data = req_imgs("img_principal_50x60")
			path = default_storage.save('img_uploads/'+unicode(data.name), ContentFile(data.read()))
			med.imagen = FileObject(path)
			med.horizontal = False
			med.save()

		#Enviar correo al administrador para que apruebe el diseño.
		from django.core.mail import EmailMultiAlternatives
		from django.template.loader import render_to_string
		from django.template import Context

		subject, from_email, to = u'Diseño aprobado','Canobba <hola@canobba.com>', RECEIVER
		context = "<p style='color:#434343'>Prueba<br>"
		context += "Texto de prueba.<br>"
		context += u"<h5 align='center'>Correo al usuario cuando se aprueba su diseño</h5><br>"
		context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
		context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
		context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
		html_content = render_to_string('email_info.html', {'asunto':u"Hola %s, su diseño ha sido aprobado!" % diseno.usuario.nombre,
													'context': context})
		msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
		msg.attach_alternative(html_content, "text/html")
		msg.send()

		messages.add_message(request, messages.SUCCESS, U"Diseño publicado correctamente.")
		return redirect("ver_perfil", disenador.profile_url)

	lista = []
	for im in range(0,8):
		lista.append(get_imagen(im+1, diseno))

	vars = {
		"title":"Subir Diseño",
		"colecciones":colecciones,
		"diseno":diseno,
		"disenador":disenador,
		"lista":lista,
	}

	return render(request, "subir_diseno.html", vars)

def get_imagen(num, diseno):
	"""
	Obtiene las imagenes por medida
	"""
	try:
		img = ImagenProducto.objects.get(medida=num, producto=diseno)
	except:
		img = None

	return img

def eliminar_diseno(request, id, profile):
	"""
	Elimina un diseño.
	"""
	try:
		diseno = Producto.objects.get(id=id)
		disenador = Usuario.objects.get(profile_url=profile)
		diseno.eliminado = True
		diseno.aprobado = False
		diseno.save()
		return redirect("ver_perfil", disenador.profile_url)
	except Exception as detail:
		messages.add_message(request, messages.ERROR, U"El diseño no existe. " + str(detail))
		return redirect("home")
