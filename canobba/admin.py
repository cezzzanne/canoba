from django.contrib import admin
from django.contrib.auth.models import User
from canobba.models import *
from django.contrib.sites.models import Site
from sorl.thumbnail import get_thumbnail

class ProductoInlineImage(admin.TabularInline):
	model = ImagenProducto
	max_num = 8
	extra = 1

class ProductoInlineCategoria(admin.TabularInline):
	model = ColeccionExtra
	max_num = 8
	extra = 1

class ProductoAdmin(admin.ModelAdmin):
	def thumbnail(self, obj):
		im = get_thumbnail(obj.imagen, '50x50', quality=99)
		return u"<img src='/uploads/%s' />" % im

	thumbnail.allow_tags = True
	search_fields = ['nombre']
	list_display = ('thumbnail', 'nombre',)
	list_display_links = ('thumbnail', 'nombre',)
	#list_filter = ('coleccion',)
	fields = ('nombre', 'descripcion','imagen', 'img_horizontal', 'img_vertical', 'usuario', 'aprobado', 'eliminado')
	inlines = [ ProductoInlineImage, ProductoInlineCategoria,]

	def save_model(self, request, obj, form, change):
		obj.cliente = request.user
		obj.save()

class ColeccionAdmin(admin.ModelAdmin):
	def thumbnail(self, obj):
		im = get_thumbnail(obj.imagen, '50x50', quality=99)
		return u"<img src='/uploads/%s' />" % im

	thumbnail.allow_tags = True
	list_display = ('thumbnail', 'orden', 'nombre')
	fields = ('orden', 'nombre', 'imagen')
	list_display_links = ('thumbnail', 'orden', 'nombre')

class ImagenSliderInlineImage(admin.TabularInline):
	model = ImagenSlider
	extra = 1
	max_num = 5

class SliderAdmin(admin.ModelAdmin):
	inlines = [ ImagenSliderInlineImage, ]

class LinkFilaInlineImage(admin.TabularInline):
	model = LinkFila
	extra = 1
	max_num = 3

class FilaInicioAdmin(admin.ModelAdmin):
	inlines = [ LinkFilaInlineImage, ]

class PedidoDetalleInline(admin.TabularInline):
	model = PedidoDetalle
	extra = 0


class PedidoAdmin(admin.ModelAdmin):
	list_display = ('folio', 'fecha', 'status', 'forma_pago')
	list_display_links = ('folio', 'fecha', 'status', 'forma_pago')
	exclude = ('folio',)
	readonly_fields = ('fecha','activo','usuario','nombre','apellidos','direccion',
						'ciudad','estado','codigo_postal','telefono','email','no_exterior')

class UsuarioAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'apellidos', 'email', 'capturado', 'tipo')
	list_display_links = ('nombre', 'apellidos', 'email', 'capturado', 'tipo')
	search_fields = ['nombre', 'apellidos', 'email']
	list_filter = ('tipo',)


admin.site.register(Producto, ProductoAdmin)
admin.site.register(Coleccion, ColeccionAdmin)
admin.site.register(Material)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Slider, SliderAdmin)
admin.site.register(FilaInicio, FilaInicioAdmin)

# Unregister
#admin.site.unregister(User)
