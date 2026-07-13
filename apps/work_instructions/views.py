from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import CompanyScopedMixin
from apps.workers.models import JobPosition
from .models import InstruccionTrabajo
from .forms import InstruccionTrabajoForm


class InstruccionTrabajoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = InstruccionTrabajo
    template_name = 'work_instructions/list.html'
    context_object_name = 'instrucciones'
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
            qs = qs.filter(titulo__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['total'] = InstruccionTrabajo.objects.filter(company=empresa).count()
            ctx['puestos'] = JobPosition.objects.filter(company=empresa)
        else:
            ctx['total'] = 0
            ctx['puestos'] = JobPosition.objects.none()
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class InstruccionTrabajoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = InstruccionTrabajo
    form_class = InstruccionTrabajoForm
    template_name = 'work_instructions/form.html'
    success_url = reverse_lazy('work_instructions:list')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class InstruccionTrabajoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = InstruccionTrabajo
    form_class = InstruccionTrabajoForm
    template_name = 'work_instructions/form.html'
    success_url = reverse_lazy('work_instructions:list')


class InstruccionTrabajoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = InstruccionTrabajo
    template_name = 'work_instructions/confirm_delete.html'
    success_url = reverse_lazy('work_instructions:list')


class InstruccionTrabajoDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = InstruccionTrabajo
    template_name = 'work_instructions/detail.html'
    context_object_name = 'instruccion'
