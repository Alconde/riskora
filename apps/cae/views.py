from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.utils import timezone

from apps.core.mixins import CompanyScopedMixin
from .models import (
    EmpresaSubcontrata, DocumentoCAE, DocumentoCAETipo,
    ProcedimientoCAE, CartaCAE, DocumentoRiesgosCAE,
)
from .forms import (
    EmpresaSubcontrataForm, DocumentoCAEForm,
    ProcedimientoCAEForm, CartaCAEForm, DocumentoRiesgosCAEForm,
)


class DashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'cae/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['empresas'] = EmpresaSubcontrata.objects.filter(empresa=empresa, activa=True)
            ctx['procedimiento'] = ProcedimientoCAE.objects.filter(empresa=empresa).first()
            ctx['carta'] = CartaCAE.objects.filter(empresa=empresa).first()
            ctx['riesgos'] = DocumentoRiesgosCAE.objects.filter(empresa=empresa).first()
        return ctx


class EmpresaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EmpresaSubcontrata
    template_name = 'cae/empresa_list.html'
    context_object_name = 'empresas'

    def get_queryset(self):
        empresa = self.get_active_company()
        if not empresa:
            return EmpresaSubcontrata.objects.none()
        return EmpresaSubcontrata.objects.filter(empresa=empresa)


class EmpresaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EmpresaSubcontrata
    template_name = 'cae/empresa_detail.html'
    context_object_name = 'empresa_sub'

    def get_queryset(self):
        empresa = self.get_active_company()
        if not empresa:
            return EmpresaSubcontrata.objects.none()
        return EmpresaSubcontrata.objects.filter(empresa=empresa)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa_sub = self.object
        tipos = DocumentoCAETipo.objects.filter(activo=True)
        docs_existentes = {
            d.tipo_documento_id: d
            for d in DocumentoCAE.objects.filter(empresa_subcontrata=empresa_sub)
        }
        documentos = []
        for tipo in tipos:
            doc = docs_existentes.get(tipo.id)
            documentos.append({
                'tipo': tipo,
                'documento': doc,
                'subido': doc.subido if doc else False,
                'actualizado': doc.actualizado if doc else False,
            })
        ctx['documentos'] = documentos
        ctx['habilitada'] = empresa_sub.habilitada
        ctx['porcentaje'] = empresa_sub.porcentaje_documentacion
        return ctx


class EmpresaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EmpresaSubcontrata
    form_class = EmpresaSubcontrataForm
    template_name = 'cae/empresa_form.html'
    success_url = reverse_lazy('cae:empresa-list')

    def form_valid(self, form):
        form.instance.empresa = self.get_active_company()
        return super().form_valid(form)


class EmpresaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EmpresaSubcontrata
    form_class = EmpresaSubcontrataForm
    template_name = 'cae/empresa_form.html'

    def get_queryset(self):
        empresa = self.get_active_company()
        if not empresa:
            return EmpresaSubcontrata.objects.none()
        return EmpresaSubcontrata.objects.filter(empresa=empresa)

    def get_success_url(self):
        return reverse_lazy('cae:empresa-detail', kwargs={'pk': self.object.pk})


class EmpresaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EmpresaSubcontrata
    template_name = 'cae/empresa_confirm_delete.html'
    success_url = reverse_lazy('cae:empresa-list')

    def get_queryset(self):
        empresa = self.get_active_company()
        if not empresa:
            return EmpresaSubcontrata.objects.none()
        return EmpresaSubcontrata.objects.filter(empresa=empresa)


class DocumentoCAEUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = DocumentoCAE
    form_class = DocumentoCAEForm
    template_name = 'cae/documento_form.html'

    def get_queryset(self):
        empresa = self.get_active_company()
        if not empresa:
            return DocumentoCAE.objects.none()
        return DocumentoCAE.objects.filter(empresa_subcontrata__empresa=empresa)

    def form_valid(self, form):
        if form.cleaned_data.get('documento'):
            form.instance.fecha_subida = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cae:empresa-detail', kwargs={'pk': self.object.empresa_subcontrata_id})


def download_documento_cae(request, pk):
    doc = DocumentoCAE.objects.filter(pk=pk).first()
    if not doc or not doc.documento:
        raise Http404
    return FileResponse(doc.documento.open('rb'), as_attachment=True, filename=doc.documento.name.split('/')[-1])


def download_procedimiento_cae(request, empresa_id):
    proc = ProcedimientoCAE.objects.filter(empresa_id=empresa_id).first()
    if not proc or not proc.documento:
        raise Http404
    return FileResponse(proc.documento.open('rb'), as_attachment=True, filename=proc.documento.name.split('/')[-1])


def download_carta_cae(request, empresa_id):
    carta = CartaCAE.objects.filter(empresa_id=empresa_id).first()
    if not carta or not carta.documento:
        raise Http404
    return FileResponse(carta.documento.open('rb'), as_attachment=True, filename=carta.documento.name.split('/')[-1])


def download_riesgos_cae(request, empresa_id):
    riesgos = DocumentoRiesgosCAE.objects.filter(empresa_id=empresa_id).first()
    if not riesgos or not riesgos.documento:
        raise Http404
    return FileResponse(riesgos.documento.open('rb'), as_attachment=True, filename=riesgos.documento.name.split('/')[-1])


class ProcedimientoCAEUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    form_class = ProcedimientoCAEForm
    template_name = 'cae/seccion_form.html'
    success_url = reverse_lazy('cae:dashboard')

    def get_object(self, queryset=None):
        empresa = self.get_active_company()
        obj, _ = ProcedimientoCAE.objects.get_or_create(empresa=empresa)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Procedimiento de Coordinacion'
        return ctx


class CartaCAEUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    form_class = CartaCAEForm
    template_name = 'cae/seccion_form.html'
    success_url = reverse_lazy('cae:dashboard')

    def get_object(self, queryset=None):
        empresa = self.get_active_company()
        obj, _ = CartaCAE.objects.get_or_create(empresa=empresa)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Carta de Empresas'
        return ctx


class DocumentoRiesgosCAEUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    form_class = DocumentoRiesgosCAEForm
    template_name = 'cae/seccion_form.html'
    success_url = reverse_lazy('cae:dashboard')

    def get_object(self, queryset=None):
        empresa = self.get_active_company()
        obj, _ = DocumentoRiesgosCAE.objects.get_or_create(empresa=empresa)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Documento de Riesgos, Medidas Preventivas y de Emergencia'
        return ctx
