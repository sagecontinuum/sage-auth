from django.urls import path
from . import views
from . import user_api

urlpatterns = [
    path('', views.home, name='home'),
    path('user_profile/<str:sage_username>', user_api.UserProfile.as_view()),
    path('token_info/', views.TokenInfo.as_view()),
    path('create-profile/', views.create_profile),
    path('portal-logout/', views.portal_logout),
    path('token/', views.token),
]
