from django.template.defaulttags import url
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    # path('register/', registration_view),
    path('apis/login/', obtain_auth_token),
    path('', HomePageView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
]