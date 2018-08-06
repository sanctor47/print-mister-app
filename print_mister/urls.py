from django.contrib import admin
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url('', include('apps.pages.urls')),
    url(r'^accounts/', include('apps.clients.urls')),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^orders/', include('apps.print_orders.urls')),
    url('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
