"""
URL Configuration for Study Management Tool project.
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('apps.ui.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('apps.core.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.courses.urls')),
    path('api/', include('apps.tasks.urls')),
    path('api/', include('apps.deadlines.urls')),
    path('api/', include('apps.plans.urls')),
    path('api/', include('apps.overview.urls')),
    path('api/', include('apps.materials.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

