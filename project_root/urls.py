
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('myapp/' ,  include('myapp.urls')), 
    path('owner/', include('owner.urls')),
    path('auth/', include('user_auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)