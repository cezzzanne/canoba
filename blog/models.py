# -*- encoding: utf-8 -*-
from django.db import models
from canobba.models import Usuario
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField
import datetime

class Categoria(models.Model):
	nombre = models.CharField(max_length=255)
	slug = models.SlugField(max_length=300)

	def __unicode__(self):
		return self.nombre

	def save(self, *args, **kwargs):
		if not self.id:
			now = datetime.datetime.now()
			self.slug = slugify(self.nombre) + "-" + str(now.second)
		super(Categoria, self).save(*args, **kwargs)

class Entrada(models.Model):
	categoria = models.ForeignKey(Categoria, related_name='entradas', on_delete=models.CASCADE)
	usuario = models.ForeignKey(Usuario, related_name='entradas', on_delete=models.CASCADE)
	titulo = models.CharField(max_length=255)
	imagen = FileBrowseField("Imagen principal", max_length=200, directory="blog/", extensions=[".jpg", ".png", ".gif"], blank=True, null=True)
	contenido = models.TextField(blank=True, null=True)
	fecha = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(max_length=300)

	def __unicode__(self):
		return self.titulo

	def save(self, *args, **kwargs):
		if not self.id:
			now = datetime.datetime.now()
			self.slug = slugify(self.titulo) + "-" + str(now.second)
		super(Entrada, self).save(*args, **kwargs)

"""
class Comentario(models.Model):
	entrada = models.ForeignKey(Entrada, related_name='observaciones')
	nombre = models.CharField(max_length=255, blank=True)
	comentarios = models.TextField(blank=True)
	fecha = models.DateTimeField(auto_now_add=True)
"""
