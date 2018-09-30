# -*- coding: utf-8 -*-
from filebrowser.sites import site
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Website:
    url(r'^$', 'canobba.views.home', name='home'),
    url(r'^colecciones/$', 'canobba.views.colecciones', name='colecciones'),
    url(r'^materiales/$', 'canobba.views.materiales', name='materiales'),
    url(r'^coleccion/(?P<col_slug>[-\w]+)/$', 'canobba.views.coleccion', name='coleccion'),
    url(r'^diseno/(?P<diseno_slug>[-\w]+)/$', 'canobba.views.diseno', name='diseno'),
    url(r'^buscar/$', 'canobba.views.buscar', name='buscar'),
    url(r'^contacto/$', 'canobba.views.contacto', name='contacto'),
    # blog
    url(r'^diario/', include('blog.urls')),

    # Auth
    url(r'^login/$', 'canobba.views.login_form', name='login_form'),
    url(r'^logout/$', 'canobba.views.logout_user', name='logout_user'),
    url(r'^registro/$', 'canobba.views.registro', name='registro'),
    url(r'^reset_pass/$', 'canobba.views.reset_pass', name='reset_pass'),
    url(r'^recover_pass/$', 'canobba.views.recover_pass', name='recover_pass'),

    # SHOPPING CART
    url(r'^add_session_cart/$', 'canobba.views.add_session_cart', name='add_session_cart'),
    url(r'^mi_carrito/$', 'canobba.views.show_cart', name='show_cart'),
    url(r'^del_cart_product/(.*)/$', 'canobba.views.remove_session_cart', name='remove_session_cart'),
    url(r'^set_qty/$', 'canobba.views.set_qty_cart', name='set_qty_cart'),

    # Pedido y Datos de envio
    url(r'^guardar_datos_envio/$', 'canobba.views.guardar_datos_envio', name='guardar_datos_envio'),
    url(r'^generar_pedido/$', 'canobba.views.generar_pedido', name='generar_pedido'),
    url(r'^detalle_pedido/(.*)/$', 'canobba.views.detalle_pedido', name='detalle_pedido'),
    url(r'^mis_pedidos/$', 'canobba.views.mis_pedidos', name='mis_pedidos'),
    url(r'^deposito/(.*)/$', 'canobba.views.deposito', name='deposito'),
    url(r'^remove_wishlist/(.*)/$', 'canobba.views.remove_wishlist', name='remove_wishlist'),
    url(r'^move_cart/(.*)/$', 'canobba.views.move_cart', name='move_cart'),

    #Paypal
    url(r'^paypal_return/(.*)/$', 'canobba.views.paypal_return', name='paypal_return'),

    # Diseñadores
    #url(r'^usuario/perfil/admin/(.*)/$', 'canobba.views.ver_perfil_admin', name='ver_perfil_admin'),
    url(r'^usuario/perfil/(.*)/$', 'canobba.views.ver_perfil', name='ver_perfil'),
    url(r'^usuario/favoritos/(.*)/$', 'canobba.views.ver_favoritos', name='ver_favoritos'),
    url(r'^follow/(.*)/$', 'canobba.views.follow', name='follow'),
    url(r'^actualizar/(.*)/$', 'canobba.views.actualizar', name='actualizar'),
    url(r'^followers/(.*)/$', 'canobba.views.followers', name='followers'),
    url(r'^following/(.*)/$', 'canobba.views.following', name='following'),
    url(r'^usuario/subir_diseno/(.*)/(.*)/$', 'canobba.views.subir_diseno', name='subir_diseno'),
    url(r'^usuario/subir_diseno/(.*)/$', 'canobba.views.subir_diseno', name='subir_diseno'),
    url(r'^usuario/eliminar_diseno/(.*)/(.*)/$', 'canobba.views.eliminar_diseno', name='eliminar_diseno'),
    #url(r'^administrar_cuadro/(?P<slug>[-\w]+)/$', 'canobba.views.administrar_cuadro', name='administrar_cuadro'),
    #url(r'^cuadro/(?P<slug>[-\w]+)/$', 'canobba.views.cuadro', name='cuadro'),
    #url(r'^cliente/(?P<slug>[-\w]+)/$', 'canobba.views.cliente', name='cliente'),
    # Rating
    url(r'^votar/(.*)/(.*)/$', 'canobba.views.votar', name='votar'),

    # AJAX
    url(r'^ajax/buscador/$', 'canobba.views.get_buscador', name='get_buscador'),
    url(r'^ajax/material/$', 'canobba.views.get_material_ajax', name='get_material_ajax'),
    url(r'^ajax/orientacion/$', 'canobba.views.get_orientacion', name='get_orientacion'),
    url(r'^ajax/profile/$', 'canobba.views.check_profile_ajax', name='check_profile_ajax'),

    #pdf
    url(r'^aviso/$', 'canobba.views.show_pdf', name='show_pdf'),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^imperavi/', include('imperavi.urls')),

    #Social
    # url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
