from django.contrib import admin
from blog.models import *
from canobba.models import Usuario
from imperavi.admin import ImperaviAdmin

class CategoriaAdmin(admin.ModelAdmin):
	exclude = ('slug',)

class EntradaAdmin(ImperaviAdmin):
    fields = ["categoria", "titulo", "imagen", "contenido"]
    list_display = ('titulo', 'fecha', 'usuario')
    list_display_links = ('titulo', 'fecha', 'usuario')

    
    def save_model(self, request, obj, form, change):
        obj.usuario = request.user
        obj.save()
    

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Entrada, EntradaAdmin)
