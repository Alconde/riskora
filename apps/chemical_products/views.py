from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import CompanyScopedMixin
from .models import ProductoQuimico, ClasificacionQuimica
from .forms import ProductoQuimicoForm, ClasificacionQuimicaForm


class ProductoQuimicoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = ProductoQuimico
    template_name = 'chemical_products/list.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        if empresa:
            qs = qs.filter(company=empresa)
        else:
            qs = qs.none()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            qs = ProductoQuimico.objects.filter(company=empresa)
            ctx['total'] = qs.count()
            ctx['total_con_ficha'] = qs.exclude(ficha_seguridad='').count()
            ctx['caducados'] = qs.filter(activo=True)
            from django.utils import timezone
            ctx['caducados_count'] = qs.filter(fecha_caducidad__lt=timezone.now().date(), activo=True).count()
        else:
            ctx['total'] = 0
            ctx['total_con_ficha'] = 0
            ctx['caducados_count'] = 0
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class ProductoQuimicoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ProductoQuimico
    form_class = ProductoQuimicoForm
    template_name = 'chemical_products/form.html'
    success_url = reverse_lazy('chemical_products:list')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class ProductoQuimicoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ProductoQuimico
    form_class = ProductoQuimicoForm
    template_name = 'chemical_products/form.html'
    success_url = reverse_lazy('chemical_products:list')


class ProductoQuimicoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = ProductoQuimico
    template_name = 'chemical_products/confirm_delete.html'
    success_url = reverse_lazy('chemical_products:list')


class ProductoQuimicoDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = ProductoQuimico
    template_name = 'chemical_products/detail.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clasificaciones'] = self.object.clasificaciones.all()
        ctx['form_clasificacion'] = ClasificacionQuimicaForm()
        return ctx


class ClasificacionQuimicaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ClasificacionQuimica
    form_class = ClasificacionQuimicaForm
    template_name = 'chemical_products/clasificacion_form.html'

    def get_success_url(self):
        return reverse_lazy('chemical_products:detail', kwargs={'pk': self.object.producto_id})

    def form_valid(self, form):
        form.instance.producto = ProductoQuimico.objects.get(pk=self.kwargs['producto_pk'])
        return super().form_valid(form)


class ClasificacionQuimicaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = ClasificacionQuimica
    template_name = 'chemical_products/clasificacion_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('chemical_products:detail', kwargs={'pk': self.object.producto_id})
