from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Q
from django.db import models
from django.http import HttpResponse
from django.utils import timezone

from apps.core.mixins import CompanyScopedMixin
from .models import CatalogoEPI, EPI, EntregaEPI, InspeccionEPI, ProcedimientoEntrega, FirmaEntrega
from .forms import (
    EPIForm, EntregaEPIForm, InspeccionEPIForm,
    ProcedimientoEntregaForm, FirmaEntregaForm, FirmaEntregaUploadForm,
)
from .services import calcular_estadisticas_epis


# =========================================================
# DASHBOARD DE EPIs
# =========================================================


class EPIDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'epis/epi_dashboard.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        stats = calcular_estadisticas_epis(empresa)
        context['stats'] = stats

        if empresa:
            context['ultimas_entregas'] = EntregaEPI.objects.filter(
                empresa=empresa
            ).select_related('epi', 'trabajador')[:5]
            context['ultimas_inspecciones'] = InspeccionEPI.objects.filter(
                empresa=empresa
            ).select_related('epi')[:5]
            context['procedimiento'] = ProcedimientoEntrega.objects.filter(
                empresa=empresa, activo=True
            ).first()
            firmas_pendientes = FirmaEntrega.objects.filter(
                empresa=empresa, estado_firma='pendiente'
            ).count()
            firmas_firmadas = FirmaEntrega.objects.filter(
                empresa=empresa, estado_firma='firmado'
            ).count()
            context['firmas_pendientes'] = firmas_pendientes
            context['firmas_firmadas'] = firmas_firmadas

        return context


# =========================================================
# PROCEDIMIENTO DE ENTREGA
# =========================================================


class ProcedimientoEntregaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ProcedimientoEntrega
    form_class = ProcedimientoEntregaForm
    template_name = 'epis/procedimiento_form.html'
    success_url = reverse_lazy('epis:dashboard')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.subido_por = self.request.user
        return super().form_valid(form)


class ProcedimientoEntregaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ProcedimientoEntrega
    form_class = ProcedimientoEntregaForm
    template_name = 'epis/procedimiento_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('epis:dashboard')


# =========================================================
# ESTADO DE FIRMAS POR TRABAJADOR
# =========================================================


class FirmaTrabajadorListView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'epis/firma_trabajador_list.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if not empresa:
            return context

        from apps.workers.models import Worker
        trabajadores = Worker.objects.filter(company=empresa).order_by('last_name', 'first_name')

        lista = []
        for t in trabajadores:
            entrega = EntregaEPI.objects.filter(
                empresa=empresa, trabajador=t, estado='activo'
            ).select_related('epi', 'epi__catalogo').first()

            firma = None
            if entrega:
                firma = FirmaEntrega.objects.filter(entrega=entrega).first()

            lista.append({
                'trabajador': t,
                'entrega': entrega,
                'firma': firma,
            })

        context['trabajadores_data'] = lista
        return context


class FirmaEntregaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = FirmaEntrega
    form_class = FirmaEntregaForm
    template_name = 'epis/firma_form.html'
    success_url = reverse_lazy('epis:firma-trabajador-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)


class FirmaEntregaUploadView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = FirmaEntrega
    form_class = FirmaEntregaUploadForm
    template_name = 'epis/firma_upload.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        form.instance.estado_firma = FirmaEntrega.EstadoFirma.FIRMADO
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('epis:firma-trabajador-list')


# =========================================================
# DESCARGA PDF REGISTRO DE ENTREGAS
# =========================================================


def descargar_registro_entregas_pdf(request):
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('/login/')

    empresa = getattr(request, 'active_company', None)

    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="registro_entregas_epi.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=14)
    subtitle_style = ParagraphStyle('Subtitle2', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'))

    nombre_empresa = empresa.legal_name if empresa else 'Catalogo de mercado'
    elements.append(Paragraph(f'Registro de EPIs - {nombre_empresa}', title_style))
    elements.append(Spacer(1, 0.3 * cm))

    usar_catalogo = False
    if empresa:
        entregas = EntregaEPI.objects.filter(empresa=empresa).select_related(
            'epi', 'epi__catalogo', 'trabajador'
        ).order_by('-fecha_entrega')
        if entregas.exists():
            data = [['Trabajador', 'EPI', 'Categoria', 'Norma EU', 'Fecha entrega', 'Caducidad', 'Estado', 'Firma']]
            for ent in entregas:
                firma = getattr(ent, 'firma', None)
                firma_estado = firma.get_estado_firma_display() if firma else 'Sin registro'
                data.append([
                    str(ent.trabajador),
                    f'{ent.epi.marca} {ent.epi.modelo}',
                    ent.epi.catalogo.get_categoria_display(),
                    ent.epi.catalogo.norma_eu,
                    str(ent.fecha_entrega),
                    str(ent.fecha_caducidad) if ent.fecha_caducidad else '-',
                    ent.get_estado_display(),
                    firma_estado,
                ])
        else:
            usar_catalogo = True
    else:
        usar_catalogo = True

    if usar_catalogo:
        elements.append(Paragraph('No hay entregas registradas. Listado del catalogo de EPIs del mercado:', subtitle_style))
        elements.append(Spacer(1, 0.3 * cm))
        catalogo = CatalogoEPI.objects.filter(activo=True)
        data = [['Nombre', 'Categoria', 'Riesgos que protege', 'Norma UNE / EN']]
        for cat in catalogo:
            data.append([
                cat.nombre,
                cat.get_categoria_display(),
                cat.riesgos_proteccion,
                cat.norma_eu,
            ])

    if len(data) == 1:
        data.append(['-', '-', '-', '-'])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdfa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    doc.build(elements)
    return response


# =========================================================
# CATALOGO DE EPIs DEL MERCADO
# =========================================================


class CatalogoEPIListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = CatalogoEPI
    template_name = 'epis/catalogo_list.html'
    context_object_name = 'catalogo'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = CatalogoEPI.objects.filter(activo=True)

        q = self.request.GET.get('q', '').strip()
        categoria = self.request.GET.get('categoria', '').strip()
        norma = self.request.GET.get('norma', '').strip()

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(riesgos_proteccion__icontains=q) |
                Q(norma_eu__icontains=q)
            )
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if norma:
            queryset = queryset.filter(norma_eu__icontains=norma)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['categoria_choices'] = CatalogoEPI.Categoria.choices
        return context


class CatalogoEPIDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = CatalogoEPI
    template_name = 'epis/catalogo_detail.html'
    context_object_name = 'item'
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# INVENTARIO DE EPIs (empresa)
# =========================================================


class EPIListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EPI
    template_name = 'epis/epi_list.html'
    context_object_name = 'epis'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = EPI.objects.select_related('empresa', 'catalogo')
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        catalogo = self.request.GET.get('catalogo', '').strip()

        if q:
            queryset = queryset.filter(
                Q(marca__icontains=q) |
                Q(modelo__icontains=q) |
                Q(numero_serie__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if catalogo:
            queryset = queryset.filter(catalogo_id=catalogo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = EPI.Estado.choices
        context['catalogo_items'] = CatalogoEPI.objects.filter(activo=True)
        context['stats'] = calcular_estadisticas_epis(self.get_active_company())
        return context


class EPIDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EPI
    template_name = 'epis/epi_detail.html'
    context_object_name = 'epi'
    login_url = '/login/'
    company_field_name = 'empresa'


class EPICreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EPI
    form_class = EPIForm
    template_name = 'epis/epi_form.html'
    success_url = reverse_lazy('epis:epi-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class EPIUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EPI
    form_class = EPIForm
    template_name = 'epis/epi_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('epis:epi-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class EPIDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EPI
    template_name = 'epis/epi_confirm_delete.html'
    success_url = reverse_lazy('epis:epi-list')
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# ENTREGAS DE EPI
# =========================================================


class EntregaEPIListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EntregaEPI
    template_name = 'epis/entrega_list.html'
    context_object_name = 'entregas'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = EntregaEPI.objects.select_related(
            'empresa', 'epi', 'epi__catalogo', 'trabajador',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        trabajador = self.request.GET.get('trabajador', '').strip()

        if q:
            queryset = queryset.filter(
                Q(epi__marca__icontains=q) |
                Q(epi__modelo__icontains=q) |
                Q(trabajador__first_name__icontains=q) |
                Q(trabajador__last_name__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if trabajador:
            queryset = queryset.filter(trabajador_id=trabajador)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = EntregaEPI.Estado.choices
        empresa = self.get_active_company()
        if empresa:
            from apps.workers.models import Worker
            context['trabajadores'] = Worker.objects.filter(company=empresa)
        return context


class EntregaEPIDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EntregaEPI
    template_name = 'epis/entrega_detail.html'
    context_object_name = 'entrega'
    login_url = '/login/'
    company_field_name = 'empresa'


class EntregaEPICreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EntregaEPI
    form_class = EntregaEPIForm
    template_name = 'epis/entrega_form.html'
    success_url = reverse_lazy('epis:entrega-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.entregado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class EntregaEPIUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EntregaEPI
    form_class = EntregaEPIForm
    template_name = 'epis/entrega_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('epis:entrega-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class EntregaEPIDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EntregaEPI
    template_name = 'epis/entrega_confirm_delete.html'
    success_url = reverse_lazy('epis:entrega-list')
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# INSPECCIONES DE EPI
# =========================================================


class InspeccionEPIListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = InspeccionEPI
    template_name = 'epis/inspeccion_list.html'
    context_object_name = 'inspecciones'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = InspeccionEPI.objects.select_related(
            'empresa', 'epi', 'epi__catalogo', 'entrega', 'inspeccionado_por',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        resultado = self.request.GET.get('resultado', '').strip()

        if q:
            queryset = queryset.filter(
                Q(epi__marca__icontains=q) |
                Q(epi__modelo__icontains=q) |
                Q(observaciones__icontains=q)
            )
        if resultado:
            queryset = queryset.filter(resultado=resultado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['resultado_choices'] = InspeccionEPI.Resultado.choices
        return context


class InspeccionEPIDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = InspeccionEPI
    template_name = 'epis/inspeccion_detail.html'
    context_object_name = 'inspeccion'
    login_url = '/login/'
    company_field_name = 'empresa'


class InspeccionEPICreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = InspeccionEPI
    form_class = InspeccionEPIForm
    template_name = 'epis/inspeccion_form.html'
    success_url = reverse_lazy('epis:inspeccion-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.inspeccionado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class InspeccionEPIUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = InspeccionEPI
    form_class = InspeccionEPIForm
    template_name = 'epis/inspeccion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('epis:inspeccion-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class InspeccionEPIDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = InspeccionEPI
    template_name = 'epis/inspeccion_confirm_delete.html'
    success_url = reverse_lazy('epis:inspeccion-list')
    login_url = '/login/'
    company_field_name = 'empresa'
