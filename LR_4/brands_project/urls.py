from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('brands_app.urls', namespace='brands_app')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
