# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from tinymce.models import HTMLField
from filebrowser.fields import FileBrowseField
from taggit.managers import TaggableManager
import datetime
import string
from decimal import *
import random

# Custom user
from django.contrib.auth.models import AbstractBaseUser, User, UserManager, BaseUserManager


def generar_folio(size=14, chars=string.ascii_uppercase + string.digits):
	'''
	Genera los folios para referenciar los pedidos
	'''
	return ''.join(random.choice(chars) for _ in range(size))

class MyCustomUserManager(BaseUserManager):
	"""
	Clase para crear usuarios y superusuarios.
	"""
	def create_user(self, email, password=None):
		"""
		Crea un usuario.
		"""

		user = self.model(
			email=email,
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password):
		"""
		Crea un superusuario.
		"""
		u = self.create_user(email, password=password)
		u.is_admin = True
		u.save(using=self._db)
		return u

class Usuario(AbstractBaseUser):
	"""
	Clase nueva para los usuarios.
	"""
	CLIENTE = (
		(0, 'Admin'),
		(1, 'Cliente'),
		(2, 'Diseñador'),
	)

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
	nombre = models.CharField(max_length=255)
	apellidos = models.CharField(max_length=255, blank=True)
	email = models.EmailField(max_length=255, unique=True, db_index=True)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	capturado = models.DateTimeField(auto_now_add=True)

	#ALTER TABLE "canobba_usuario" ADD COLUMN "tipo" integer NOT NULL DEFAULT 0;
	tipo = models.IntegerField(choices=CLIENTE, default=0)
	#Datos de facturacion
	rfc = models.CharField(max_length=255, null=True, blank=True)
	razon_social = models.CharField(max_length=255, null=True, blank=True)
	calle = models.CharField(max_length=255, null=True, blank=True)
	no_exterior = models.IntegerField(null=True, blank=True)
	no_interior = models.IntegerField(null=True, blank=True)
	codigo_postal = models.IntegerField(null=True, blank=True)
	colonia = models.CharField(max_length=255, null=True, blank=True)
	localidad = models.CharField(max_length=255, null=True, blank=True)
	municipio = models.CharField(max_length=255, null=True, blank=True)
	estado = models.CharField(max_length=255, null=True, blank=True)
	telefono = models.CharField(max_length=255, null=True, blank=True)
	#Datos del diseñador
	biografia = models.TextField(null=True, blank=True)
	descripcion_trabajo = models.TextField(null=True, blank=True)
	tecnicas = models.TextField(null=True, blank=True)
	#ALTER TABLE "canobba_usuario" ADD COLUMN "imagen" varchar(100);
	imagen = models.ImageField(upload_to="imagen_diseno", null=True, blank=True)
	#ALTER TABLE "canobba_usuario" ADD COLUMN "profile_url" varchar(255) UNIQUE;
	profile_url = models.CharField(max_length=255, null=True, blank=True, unique=True)

	# objects = MyCustomUserManager()

	USERNAME_FIELD = 'email'


	def get_full_name(self):
		# The user is identified by their email address
		return self.nombre + " " + self.apellidos

	def get_short_name(self):
		# The user is identified by their email address
		return self.nombre

	def __unicode__(self):
		return self.nombre

	def has_perm(self, perm, obj=None):
		"Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
		return True

	def has_module_perms(self, app_label):
		"Does the user have permissions to view the app `app_label`?"
		# Simplest possible answer: Yes, always
		return True

	@property
	def is_staff(self):
		"Is the user a member of staff?"
		# Simplest possible answer: All admins are staff
		return self.is_admin

	def __unicode__(self):
		return self.nombre

	# def save(self, *args, **kwargs):
		#self.set_password(self.password)
		# super(Usuario, self).save(*args, **kwargs)

	def get_rating(self):
		"""
		Calcula y regresa el rating del diseñador.
		"""
		acum = 0
		for rating in self.ratings.all():
			acum += rating.rating

		if self.ratings.count() == 0:
			rating = 0
		else:
			rating = int(acum / self.ratings.count())
		return rating

	def get_followers(self):
		"""
		Obtiene el numero de seguidores de este diseñador.
		"""
		return self.followers.count()

	def get_following(self):
		"""
		Obtiene el numero de diseñadores a los que este diseñador sigue.
		"""
		return self.siguiendo.count()

class Coleccion(models.Model):
	nombre = models.CharField(max_length=300)
	slug = models.SlugField(max_length=150)
	imagen = FileBrowseField("Imagen", max_length=200, help_text='300x500 px',
							directory="colecciones/",
							extensions=[".jpg", ".gif", ".png"],
							blank=True, null=True)
                            # tags = TaggableManager(blank=True)

	# Se utiliza para mostrar el orden de las categorias en el sitio
	orden = models.IntegerField(max_length=10, default=0, unique=True)

	def __unicode__(self):
		return self.nombre

	def save(self, *args, **kwargs):
		if not self.id:
			now = datetime.datetime.now()
			self.slug = slugify(self.nombre) + "-" + str(now.second)
		super(Coleccion, self).save(*args, **kwargs)

	class Meta:
		verbose_name = 'Colección'
		verbose_name_plural = 'Colecciones'

class Producto(models.Model):

	ORIENTACION = (
		(1, "Horizontal"),
		(2, "Vertical")
		)

	# ALTER TABLE "canobba_producto" ADD COLUMN "usuario_id" integer REFERENCES "canobba_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
	usuario = models.ForeignKey(Usuario, null=True, blank=True, related_name='disenos', on_delete=models.CASCADE)
	#coleccion = models.ForeignKey(Coleccion, verbose_name=u'Colección')
	#ALTER TABLE "canobba_producto" DROP COLUMN "coleccion";
	nombre = models.CharField(max_length=300)
	slug = models.SlugField(max_length=150)
	descripcion = HTMLField(blank=True, null=True)

	imagen = FileBrowseField("Imagen principal", help_text='Usar mismas medidas del de 300x350 px',
							max_length=200, directory="productos/disenos/",
							extensions=[".jpg", ".gif", ".png"],
							blank=True, null=True)
	img_horizontal = FileBrowseField("Imagen horizontal", help_text='200x120 px (Necesaria para wishlist y carrito)',
									max_length=200, directory="productos/disenos/horizontal/",
									extensions=[".jpg", ".gif", ".png"],
									blank=True, null=True)
	img_vertical = FileBrowseField("Imagen vertical", help_text='120x200 px (Necesaria para wishlist y carrito)',
									max_length=200, directory="productos/disenos/vertical/",
									extensions=[".jpg", ".gif", ".png"],
									blank=True, null=True)

	capturado = models.DateTimeField(auto_now_add=True)
    #tags = TaggableManager(blank=True)

	#26/03/15
	#ALTER TABLE "canobba_producto" ADD COLUMN "aprobado" boolean NOT NULL DEFAULT false;
	aprobado = models.BooleanField(default=False)
	#ALTER TABLE "canobba_producto" ADD COLUMN "eliminado" boolean NOT NULL DEFAULT false;
	eliminado = models.BooleanField(default=False)

	def get_precio(id):
		pass

	def __unicode__(self):
		return self.nombre

	def save(self, *args, **kwargs):
		if not self.id:
			now = datetime.datetime.now()
			self.slug = slugify(self.nombre) + "-" + str(now.second)
		#Enviar un email al cliente y al administrador cuando el diseno ha sido aprovado
		if self.aprobado and self.usuario:
			from django.core.mail import EmailMultiAlternatives
			from django.template.loader import render_to_string
			from django.template import Context

			subject, from_email, to = u'Diseño aprobado','Canobba <hola@canobba.com>', self.usuario.email
			context = "<p style='color:#434343'>Prueba<br>"
			context += "Texto de prueba.<br>"
			context += u"<h5 align='center'>Correo al usuario cuando se aprueba su diseño</h5><br>"
			context += "Quedamos a sus ordenes y como siempre es un placer servirle.<br><br>"
			context += "No olvide seguirnos en nuestras redes sociales <a href='http://instagram.com/canobba'>Instagram</a>, "
			context += "<a href='https://twitter.com/canobba'>Twitter</a> and <a href='https://www.facebook.com/canobba'>Facebook</a></p>"
			html_content = render_to_string('email_info.html', {'asunto':u"Hola %s, su diseño ha sido aprobado!" % self.usuario.nombre,
														'context': context})
			msg = EmailMultiAlternatives(subject, html_content, from_email, [to,])
			msg.attach_alternative(html_content, "text/html")
			msg.send()
		super(Producto, self).save(*args, **kwargs)

	class Meta:
		verbose_name = 'Diseño'
		verbose_name_plural = 'Diseños'

class ImagenProducto(models.Model):
	MEDIDAS = (
		(1,"50cm x 60cm"),
		(2,"60cm x 90cm"),
		(3,"70cm x 70cm"),
		(4,"80cm x 120cm"),
		(5,"100cm x 100cm"),
		(6,"100cm x 150cm"),
		(7,"115cm x 180cm"),
		(8,"200cm x 120cm")
	)

	medida = models.IntegerField(max_length=10, choices=MEDIDAS, default=1)
	producto = models.ForeignKey(Producto, related_name='imagenes', on_delete=models.CASCADE)
	imagen = FileBrowseField("Imagen", max_length=200, directory="productos/", extensions=[".jpg", ".png", ".jpeg", ".gif"], blank=True, null=True)
	horizontal = models.BooleanField(verbose_name=u'horizontal')

	def save(self, *args, **kwargs):
		try:
			med = ImagenProducto.objects.get(medida=self.medida, producto=self.producto)
		except:
			super(ImagenProducto, self).save(*args, **kwargs)

class Material(models.Model):
	'''
	Modelo donde se definen los precios dependiendo de la medida y el material.
	'''
	MATERIALES = (
		(1, "Lienzo Liso"),
		(2, "Texturizado"),
		(3, "Canvas"),
		(4, "Vinipiel")
		)
	material = models.IntegerField(max_length=5, choices=MATERIALES)
	precio1 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'50cm x 60cm', default="0.00")
	precio2 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'60cm x 90cm', default="0.00")
	precio3 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'70cm x 70cm', default="0.00")
	precio4 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'80cm x 120cm', default="0.00")
	precio5 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'100cm x 100cm', default="0.00")
	precio6 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'100cm x 150cm', default="0.00")
	precio7 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'115cm x 180cm', default="0.00")
	precio8 = models.DecimalField(max_digits=1000, decimal_places=2, verbose_name=u'200cm x 120cm', default="0.00")

	def __unicode__(self):
		return self.get_material_display()

	class Meta:
		verbose_name_plural = 'Lista de precios'
		verbose_name = 'Lista de precios'

class Slider(models.Model):
	'''
	Modelo para administrar el slider principal
	'''
	nombre = models.CharField(max_length=255)

	def __unicode__(self):
		return self.nombre

class ImagenSlider(models.Model):
	slider = models.ForeignKey(Slider, related_name='imagenes', on_delete=models.CASCADE)
	imagen = FileBrowseField("Imagen principal", help_text='Medidas recomendadas 1143px x 400px',
							max_length=400, directory="slider/",
							extensions=[".jpg", ".gif", ".png"],
							blank=True, null=True)
	texto = models.CharField(max_length=350, blank=True, null=True, help_text='Texto que aparecerá sobre la imagen')

class ProductoCarrito(models.Model):
	'''
	Modelo que se utiliza para el carrito (contiene los detalles del producto)
	'''
	producto = models.ForeignKey(Producto, related_name='carrito', on_delete=models.CASCADE)
	material = models.ForeignKey(Material, on_delete=models.CASCADE)
	medida = models.CharField(max_length=255)
	orientacion = models.CharField(max_length=255)
	precio = models.DecimalField(max_digits=1000, decimal_places=2, default="0.00")

	def __unicode__(self):
		return self.producto.nombre

	class Meta:
		verbose_name = 'Diseño'
		verbose_name_plural = 'Diseños'


class FilaInicio(models.Model):
	nombre = models.CharField(max_length=255)

	def __unicode__(self):
		return self.nombre

	class Meta:
		verbose_name = 'Fila de enlaces del inicio'
		verbose_name_plural = 'Fila de enlaces del inicio'


class LinkFila(models.Model):

	TIPOS = (
	(1, "1 columna 390x280px"),
	(2, "2 columnas 780x280px"),
	)

	tipo = models.IntegerField(max_length=10, choices=TIPOS, default=3, verbose_name='Numero de filas')
	fila = models.ForeignKey(FilaInicio, related_name='links', on_delete=models.CASCADE)
	imagen = FileBrowseField("Imagen", max_length=400,
							directory="index/",
							extensions=[".jpg", ".gif", ".png"],
							blank=True, null=True)

	descripcion = models.CharField(max_length=255, blank=True)
	url = models.URLField(max_length=255, blank=True, null=True, help_text='ejemplo: http://canobba.com')

	def get_css(self):
		if self.tipo == 1:
			return "col-md-4"
		if self.tipo == 2:
			return "col-md-8"
	class Meta:
		verbose_name = 'Enlace'


class Pedido(models.Model):
	STATUS = (
		(0, "Pendiente"),
		(1, "Pagado"),
		(2, "Cancelado"),
	)

	def folio():
		if Pedido.objects.all().count() == 0:
			num_fol = 1
			return num_fol

		num_fol = Pedido.objects.order_by('-folio')[0].folio
		if not num_fol:
			return 1
		else:
			return num_fol + 1

	folio = models.IntegerField(unique=True, default=folio)
	fecha = models.DateTimeField(auto_now_add=True)
	activo = models.BooleanField(default=True)
	status = models.IntegerField(choices=STATUS, default=0)
	#subtotal = models.DecimalField(max_digits=1000, decimal_places=2, default="0.00")
	#total = models.DecimalField(max_digits=1000, decimal_places=2, default="0.00")

	#Datos de envio
	usuario = models.ForeignKey(Usuario, related_name='pedidos', null=True, blank=True, on_delete=models.CASCADE)
	nombre = models.CharField(max_length=255, null=True, blank=True)
	apellidos = models.CharField(max_length=255, null=True, blank=True)
	direccion = models.CharField(max_length=255, null=True, blank=True)
	ciudad = models.CharField(max_length=255, null=True, blank=True)
	estado = models.CharField(max_length=255, null=True, blank=True)
	codigo_postal = models.CharField(max_length=6, null=True, blank=True)
	telefono = models.CharField(max_length=100, null=True, blank=True)
	email = models.EmailField(max_length=255, null=True, blank=True)
	no_exterior = models.CharField(max_length=20, null=True, blank=True)
	forma_pago = models.CharField(max_length=255, null=True, blank=True)
	#Campos 24/03/15
	#ALTER TABLE "canobba_pedido" ADD COLUMN "no_interior" varchar(20);
	#ALTER TABLE "canobba_pedido" ADD COLUMN "colonia" varchar(255);
	no_interior = models.CharField(max_length=20, null=True, blank=True)
	colonia = models.CharField(max_length=255, null=True, blank=True)

	def get_total(self):
		"""
		Regresa el total del pedido con iva incluido.
		"""
		total = 0
		for detalle in self.detalles.all():
			total += detalle.get_total()
		return total

	def get_total_siniva(self):
		"""
		Regresa el total del pedido menos el iva.
		"""
		return self.get_total() / Decimal(1.16)

	def get_iva(self):
		"""
		Regresa el iva sobre el total del pedido.
		"""
		return self.get_total_siniva() * Decimal(0.16)

	def get_status_css(self):
		if self.status == 0:
			return "info"
		if self.status == 1:
			return "success"
		if self.status == 2:
			return "danger"

	def get_forma_pago(self):
		"""
		Regresa la forma con la que se pagó el pedido.
		"""
		if self.forma_pago == "Conekta":
			return "VISA/MASTERCARD"
		return self.forma_pago

class PedidoDetalle(models.Model):
	pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
	producto = models.ForeignKey(ProductoCarrito, on_delete=models.CASCADE)
	cantidad = models.IntegerField()

	def get_total(self):
		return self.producto.precio * Decimal(self.cantidad)

	class Meta:
		verbose_name = 'Diseño'
		verbose_name_plural = 'Detalles del Pedido'

class WishlistDetalle(models.Model):
	usuario = models.ForeignKey(Usuario, related_name='wishlist', on_delete=models.CASCADE)
	producto = models.ForeignKey(ProductoCarrito, on_delete=models.CASCADE)

class Rating(models.Model):
	"""
	Tabla para almacenar los votos de cada diseñador.
	"""
	rating = models.IntegerField()
	disenador = models.ForeignKey(Usuario, related_name='ratings', on_delete=models.CASCADE)
	usuario = models.ForeignKey(Usuario, related_name='votos', on_delete=models.CASCADE)
	#comentario = models.TextField()
	fecha = models.DateTimeField(auto_now_add=True)

class Follower(models.Model):
	"""
	Tabla para almacenar los seguidores de cada diseñador.
	"""
	disenador = models.ForeignKey(Usuario, related_name='followers', on_delete=models.CASCADE)
	usuario = models.ForeignKey(Usuario, related_name='siguiendo', on_delete=models.CASCADE)
	fecha = models.DateTimeField(auto_now_add=True)

class ColeccionExtra(models.Model):
	"""
	Tabla para agregar colecciones extra a los diseños.
	"""
	diseno = models.ForeignKey(Producto, related_name='categorias', verbose_name='Diseño', on_delete=models.CASCADE)
	coleccion = models.ForeignKey(Coleccion, related_name='disenos', verbose_name='Colección', on_delete=models.CASCADE)
