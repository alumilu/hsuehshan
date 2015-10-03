from django.conf.urls import patterns, include, url
from django.contrib import admin
from its import views as its_views

admin.autodiscover()

#from rest_framework import routers

#router = routers.DefaultRouter()
#router.register(r'nf5qos', its_views.Nf5QosViewSet)
#router.register(r'groups', views.GroupViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hsuehshan.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^nf5qosS/$', its_views.nf5QosS),
    url(r'^nf5qosN/$', its_views.nf5QosN),

    #url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
