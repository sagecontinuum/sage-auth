"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import include, path
from . import views

from django.conf.urls import url # for native login
from django.contrib.auth import views as auth_views # for native login
from django.conf.urls import url


urlpatterns = [
    path('token_info/', views.TokenInfo.as_view()),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('django.contrib.auth.urls')), #  enable the ‘Logout’ link
    path('', include('social_django.urls', namespace='social')), # ‘Login with Globus’ link and other URLs required by OpenID Connect protocol.
    path('portal-logout/', views.portal_logout),
    path('token/', views.token),
    url('', include('django_prometheus.urls')),
]

