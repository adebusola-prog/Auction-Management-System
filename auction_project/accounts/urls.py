from django.urls import path
from . import views

urlpatterns = [
    path('access/', views.AccessAPIView.as_view(), name='access'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('admin-login/', views.AdminLoginAPIView.as_view(), name='admin_login')
]