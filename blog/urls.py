from django.conf.urls import patterns, include, url
from django.conf import settings


urlpatterns = patterns('blog.views',
    # Examples:
    url(r'^$', 'home', name='blog'),
    url(r'^entrada/(.*)/$', 'entrada', name='entrada'),
    url(r'^comentar/(.*)/$', 'comentar', name='comentar'),
    url(r'^categoria/(.*)/$', 'categoria', name='categoria'),
    url(r'^buscar/$', 'buscar', name='buscar_entrada'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
