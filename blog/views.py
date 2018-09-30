# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from blog.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

# Create your views here.
def home(request):
	entradas = Entrada.objects.all().order_by("-fecha")
	categorias = Categoria.objects.all()
	paginator = Paginator(entradas, 10) # Show 25 contacts per page

	page = request.GET.get('page')
	try:
		entradas = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		entradas = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		entradas = paginator.page(paginator.num_pages)
	vars = {"title":"Diario", "entradas":entradas, "categorias":categorias}
	return render(request, "blog/entradas.html", vars)

def entrada(request, slug):
	entrada = Entrada.objects.get(slug=slug)
	categorias = Categoria.objects.all()
	title = entrada.titulo
	#comentarios = entrada.observaciones.all()	
	vars = {"title":title, "entrada":entrada, "categorias":categorias}
	return render(request, "blog/entrada.html", vars)

def comentar(request, id):
	if request.method == "POST":
		r = request.POST.get
		ob = Observacion()
		ob.entrada = Entrada.objects.get(id=id)
		ob.nombre = r('nombre')
		ob.comentarios = r('comentarios')
		ob.save()
		messages.add_message(request, messages.SUCCESS, 'Su comentario a sido publicado.')
		return redirect("entrada", ob.entrada.slug)

def categoria(request, slug):
	categorias = Categoria.objects.all()
	categoria = Categoria.objects.get(slug=slug)
	entradas = categoria.entradas.all()
	paginator = Paginator(entradas, 10) # Show 25 contacts per page

	page = request.GET.get('page')
	try:
		entradas = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		entradas = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		entradas = paginator.page(paginator.num_pages)
	vars = {"title":categoria.nombre, "entradas":entradas, "categorias":categorias}
	return render(request, "blog/entradas.html", vars)

def buscar(request):
	s = request.GET.get("q")
	categorias = Categoria.objects.all()
	entradas = Entrada.objects.filter(titulo__icontains=s)
	paginator = Paginator(entradas, 10) # Show 25 contacts per page

	page = request.GET.get('page')
	try:
		entradas = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		entradas = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		entradas = paginator.page(paginator.num_pages)
	vars = {"title":"Blog", "entradas":entradas, "categorias":categorias}
	return render(request, "blog/entradas.html", vars)