"""covidadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from .api import api_router
from vizualization.views import SlugBlogShow,SlugStaticPageShow

# import debug_toolbar

admin.site.site_header = 'COVID-19 Procurement Explorer'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/visualization/', include('vizualization.urls')),
    path('api/contents/<str:type>/<str:slug>/',SlugBlogShow.as_view()),
    path('api/staticpage/<str:type>',SlugStaticPageShow.as_view()),
    path('', include('country.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('pages/', include(wagtail_urls)),
    path('api/v2/', api_router.urls),
    re_path(r'^', include(wagtail_urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#         urlpatterns = [
#             path('__debug__/', include(debug_toolbar.urls)),
#         ] + urlpatterns