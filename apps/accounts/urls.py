from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    ProfileView,
    PasswordChangeView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registro/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', ProfileView.as_view(), name='profile'),
    path('perfil/cambiar-contrasena/', PasswordChangeView.as_view(), name='password-change'),
]
