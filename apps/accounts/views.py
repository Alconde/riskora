from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView

from .forms import LoginForm, RegisterForm, UserProfileForm
from .models import User


class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Bienvenido, {user.get_full_name() or user.username}.')
        return super().form_valid(form)


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('dashboard'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Cuenta creada correctamente. Ya puedes iniciar sesión.'
        )
        return response

    def get_success_url(self):
        return reverse_lazy('accounts:login')


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Has cerrado sesión correctamente.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    login_url = '/login/'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/password_change.html'
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        from django.contrib.auth.forms import PasswordChangeForm
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada correctamente.')
            return HttpResponseRedirect(reverse_lazy('accounts:profile'))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        from django.contrib.auth.forms import PasswordChangeForm
        context = self.get_context_data(**kwargs)
        context['form'] = PasswordChangeForm(request.user)
        return self.render_to_response(context)
