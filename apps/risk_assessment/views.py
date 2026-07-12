from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from apps.risk_assessment.forms import (
    EvaluacionRiesgosForm,
    ItemEvaluacionRiesgosForm,
)
from apps.risk_assessment.models import (
    EvaluacionRiesgos,
    ItemEvaluacionRiesgos,
)
from apps.risk_assessment.services import (
    calcular_grado_riesgo,
    calcular_estadisticas_evaluacion,
)
from apps.companies.models import Company
from apps.core.mixins import CompanyScopedMixin


class EvaluacionRiesgosListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EvaluacionRiesgos
    template_name = 'risk_assessment/evaluacion_list.html'
    context_object_name = 'evaluaciones'
    paginate_by = 20
    login_url = '/admin/login/'
    company_field_name = 'empresa'

    def get_base_queryset(self):
        return EvaluacionRiesgos.objects.select_related(
            'empresa', 'centro_trabajo', 'revisado_por'
        )

    def get_queryset(self):
        queryset = self.get_company_scoped_queryset(self.get_base_queryset())

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()

        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(centro_trabajo__name__icontains=q)
            )

        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtros'] = self.request.GET
        context['estado_choices'] = EvaluacionRiesgos.Estado.choices
        return context


class EvaluacionRiesgosDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EvaluacionRiesgos
    template_name = 'risk_assessment/evaluacion_detail.html'
    context_object_name = 'evaluacion'
    login_url = '/admin/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        return EvaluacionRiesgos.objects.select_related(
            'empresa', 'centro_trabajo', 'revisado_por', 'aprobado_por'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.items.select_related(
            'puesto_trabajo', 'tipo_peligro', 'responsable_medida'
        )
        context['items'] = items
        context['stats'] = calcular_estadisticas_evaluacion(items)
        context['item_form'] = ItemEvaluacionRiesgosForm(
            empresa=self.object.empresa
        )
        return context


class EvaluacionRiesgosCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionRiesgos
    form_class = EvaluacionRiesgosForm
    template_name = 'risk_assessment/evaluacion_form.html'
    success_url = reverse_lazy('evaluacion-list')
    login_url = '/admin/login/'


class EvaluacionRiesgosUpdateView(LoginRequiredMixin, UpdateView):
    model = EvaluacionRiesgos
    form_class = EvaluacionRiesgosForm
    template_name = 'risk_assessment/evaluacion_form.html'
    login_url = '/admin/login/'

    def get_success_url(self):
        return reverse_lazy('evaluacion-detail', kwargs={'pk': self.object.pk})


class EvaluacionRiesgosDeleteView(LoginRequiredMixin, DeleteView):
    model = EvaluacionRiesgos
    template_name = 'risk_assessment/evaluacion_confirm_delete.html'
    success_url = reverse_lazy('evaluacion-list')
    login_url = '/admin/login/'


class ItemEvaluacionCreateView(LoginRequiredMixin, CreateView):
    model = ItemEvaluacionRiesgos
    form_class = ItemEvaluacionRiesgosForm
    template_name = 'risk_assessment/item_form.html'
    login_url = '/admin/login/'

    def get_evaluacion(self):
        return EvaluacionRiesgos.objects.get(pk=self.kwargs['evaluacion_pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        evaluacion = self.get_evaluacion()
        kwargs['empresa'] = evaluacion.empresa
        return kwargs

    def form_valid(self, form):
        evaluacion = self.get_evaluacion()
        form.instance.evaluacion = evaluacion
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'evaluacion-detail', kwargs={'pk': self.kwargs['evaluacion_pk']}
        )


class ItemEvaluacionUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemEvaluacionRiesgos
    form_class = ItemEvaluacionRiesgosForm
    template_name = 'risk_assessment/item_form.html'
    login_url = '/admin/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.object.evaluacion.empresa
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'evaluacion-detail',
            kwargs={'pk': self.object.evaluacion.pk},
        )


class ItemEvaluacionDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemEvaluacionRiesgos
    template_name = 'risk_assessment/item_confirm_delete.html'
    login_url = '/admin/login/'

    def get_success_url(self):
        return reverse_lazy(
            'evaluacion-detail',
            kwargs={'pk': self.object.evaluacion.pk},
        )


def calcular_riesgo_ajax(request):
    """Endpoint AJAX para calcular el grado de riesgo en tiempo real."""
    try:
        probabilidad = int(request.GET.get('probabilidad', 0))
        severidad = int(request.GET.get('severidad', 0))
        resultado = calcular_grado_riesgo(probabilidad, severidad)
        return JsonResponse(resultado)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Valores inválidos'}, status=400)
