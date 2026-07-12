from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, FileResponse
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
import io

from apps.risk_assessment.forms import (
    EvaluacionRiesgosForm,
    ItemEvaluacionRiesgosForm,
)
from apps.risk_assessment.models import (
    EvaluacionRiesgos,
    ItemEvaluacionRiesgos,
    TipoPeligro,
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
    login_url = '/login/'
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
    login_url = '/login/'
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


class EvaluacionRiesgosCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EvaluacionRiesgos
    form_class = EvaluacionRiesgosForm
    template_name = 'risk_assessment/evaluacion_form.html'
    success_url = reverse_lazy('risk_assessment:evaluacion-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        active_company = self.get_active_company()
        if active_company:
            form.instance.empresa = active_company
        return super().form_valid(form)


class EvaluacionRiesgosUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EvaluacionRiesgos
    form_class = EvaluacionRiesgosForm
    template_name = 'risk_assessment/evaluacion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            EvaluacionRiesgos.objects.select_related(
                'empresa', 'centro_trabajo', 'revisado_por', 'aprobado_por'
            )
        )

    def get_success_url(self):
        return reverse_lazy('risk_assessment:evaluacion-detail', kwargs={'pk': self.object.pk})


class EvaluacionRiesgosDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EvaluacionRiesgos
    template_name = 'risk_assessment/evaluacion_confirm_delete.html'
    success_url = reverse_lazy('risk_assessment:evaluacion-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            EvaluacionRiesgos.objects.select_related('empresa')
        )


class ItemEvaluacionCreateView(LoginRequiredMixin, CreateView):
    model = ItemEvaluacionRiesgos
    form_class = ItemEvaluacionRiesgosForm
    template_name = 'risk_assessment/item_form.html'
    login_url = '/login/'

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
    login_url = '/login/'

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
    login_url = '/login/'

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


# ---------------------------------------------------------------------------
# Importación / Exportación Excel
# ---------------------------------------------------------------------------

ENCabezado_EXCEL = [
    'Puesto de trabajo',
    'Tipo de peligro',
    'Factor de riesgo / condición detectada',
    'Riesgo',
    'Medidas existentes',
    'Probabilidad (1-3)',
    'Severidad (1-3)',
    'Medidas propuestas',
]


def _obtener_opciones_riesgo():
    """Devuelve dict {valor: etiqueta} de las opciones de riesgo."""
    return dict(ItemEvaluacionRiesgos.RIESGO_CHOICES)


def _obtener_opciones_prob_sev():
    prob = dict(ItemEvaluacionRiesgos.Probabilidad.choices)
    sev = dict(ItemEvaluacionRiesgos.Severidad.choices)
    return prob, sev


def exportar_excel(request, evaluacion_pk):
    """Exporta los items de una evaluación a un archivo Excel."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    evaluacion = EvaluacionRiesgos.objects.get(pk=evaluacion_pk)
    items = evaluacion.items.select_related(
        'puesto_trabajo', 'tipo_peligro'
    ).order_by('puesto_trabajo', 'factor_riesgo_condicion')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Evaluación de Riesgos'

    # Estilos
    header_font = Font(name='Arial', bold=True, size=11, color='FFFFFF')
    header_fill = PatternFill(start_color='0F172A', end_color='0F172A', fill_type='solid')
    header_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin'),
    )

    # Cabecera info
    ws.merge_cells('A1:H1')
    ws['A1'] = evaluacion.titulo
    ws['A1'].font = Font(name='Arial', bold=True, size=14)
    ws.merge_cells('A2:H2')
    ws['A2'] = (
        f'Empresa: {evaluacion.empresa} | Centro: {evaluacion.centro_trabajo} | '
        f'Fecha: {evaluacion.fecha_evaluacion.strftime("%d/%m/%Y")}'
    )
    ws['A2'].font = Font(name='Arial', size=10, color='64748B')
    ws.row_dimensions[3].height = 6

    # Cabeceras columna
    for col_num, header in enumerate(ENCabezado_EXCEL, 1):
        cell = ws.cell(row=4, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # Datos
    prob_labels, sev_labels = _obtener_opciones_prob_sev()
    riesgo_opciones = _obtener_opciones_riesgo()

    for row_num, item in enumerate(items, 5):
        data = [
            str(item.puesto_trabajo),
            str(item.tipo_peligro) if item.tipo_peligro else '',
            item.factor_riesgo_condicion,
            riesgo_opciones.get(item.riesgo, item.riesgo),
            item.medidas_existentes,
            item.probabilidad,
            item.severidad,
            item.medidas_propuestas,
        ]
        for col_num, value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(vertical='top', wrap_text=True)

    # Columnas auto-anchura
    col_widths = [25, 25, 40, 30, 35, 15, 15, 35]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    # Guardar en buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f'evaluacion_riesgos_{evaluacion.pk}.xlsx'
    response = FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    return response


def importar_excel(request, evaluacion_pk):
    """Importa items de evaluación desde un archivo Excel."""
    from openpyxl import load_workbook

    evaluacion = EvaluacionRiesgos.objects.get(pk=evaluacion_pk)

    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    archivo = request.FILES.get('archivo_excel')
    if not archivo:
        return HttpResponse('No se proporcionó archivo', status=400)

    try:
        wb = load_workbook(archivo, read_only=True)
        ws = wb.active

        # Mapear puestos de trabajo existentes
        from apps.workers.models import JobPosition
        puestos = {
            p.name: p
            for p in JobPosition.objects.filter(company=evaluacion.empresa)
        }

        # Mapear tipos de peligro
        tipos = {
            t.nombre: t
            for t in TipoPeligro.objects.filter(activo=True)
        }

        riesgo_opciones_inv = {v.lower(): k for k, v in _obtener_opciones_riesgo().items()}

        # Buscar la fila de cabecera
        start_row = 1
        for row in ws.iter_rows(min_row=1, max_row=10, max_col=1):
            for cell in row:
                if cell.value and 'puesto' in str(cell.value).lower():
                    start_row = cell.row + 1
                    break

        importados = 0
        errores = []

        for row_num, row in enumerate(ws.iter_rows(min_row=start_row, max_col=8, values_only=True)):
            if not row[0]:
                continue

            puesto_nombre = str(row[0]).strip()
            tipo_nombre = str(row[1]).strip() if row[1] else ''
            factor_riesgo = str(row[2]).strip() if row[2] else ''
            riesgo_texto = str(row[3]).strip().lower() if row[3] else ''
            medidas_existentes = str(row[4]).strip() if row[4] else ''
            probabilidad = row[5]
            severidad = row[6]
            medidas_propuestas = str(row[7]).strip() if row[7] else ''

            # Validaciones
            if not factor_riesgo:
                errores.append(f'Fila {row_num + start_row}: falta factor de riesgo')
                continue

            if not probabilidad or not severidad:
                errores.append(f'Fila {row_num + start_row}: falta probabilidad o severidad')
                continue

            try:
                probabilidad = int(probabilidad)
                severidad = int(severidad)
            except (ValueError, TypeError):
                errores.append(f'Fila {row_num + start_row}: probabilidad/severidad no son números')
                continue

            if probabilidad not in (1, 2, 3) or severidad not in (1, 2, 3):
                errores.append(f'Fila {row_num + start_row}: probabilidad/severidad fuera de rango (1-3)')
                continue

            # Buscar puesto de trabajo
            puesto = puestos.get(puesto_nombre)
            if not puesto:
                errores.append(f'Fila {row_num + start_row}: puesto "{puesto_nombre}" no encontrado')
                continue

            # Buscar tipo de peligro
            tipo_peligro = tipos.get(tipo_nombre) if tipo_nombre else None

            # Mapear riesgo
            riesgo_valor = riesgo_opciones_inv.get(riesgo_texto, '')

            # Calcular riesgo
            resultado = calcular_grado_riesgo(probabilidad, severidad)

            ItemEvaluacionRiesgos.objects.create(
                evaluacion=evaluacion,
                puesto_trabajo=puesto,
                tipo_peligro=tipo_peligro,
                factor_riesgo_condicion=factor_riesgo,
                riesgo=riesgo_valor,
                medidas_existentes=medidas_existentes,
                probabilidad=probabilidad,
                severidad=severidad,
                grado_riesgo=resultado['grado'],
                nivel_riesgo=resultado['nivel'],
                medidas_propuestas=medidas_propuestas,
            )
            importados += 1

        wb.close()

        return HttpResponse(
            f'<html><body>'
            f'<h2>Importación completada</h2>'
            f'<p>Items importados: <strong>{importados}</strong></p>'
            f'{"<p>Errores:</p><ul>" + "".join("<li>" + e + "</li>" for e in errores) + "</ul>" if errores else ""}'
            f'<p><a href="/evaluaciones/{evaluacion.pk}/">Volver a la evaluación</a></p>'
            f'</body></html>'
        )

    except Exception as e:
        return HttpResponse(f'Error al procesar el archivo: {str(e)}', status=400)


def plantilla_excel(request):
    """Descarga una plantilla Excel vacía para importar."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()
    ws = wb.active
    ws.title = 'Plantilla Evaluación'

    # Cabecera info
    ws.merge_cells('A1:H1')
    ws['A1'] = 'Plantilla de Importación - Evaluación de Riesgos'
    ws['A1'].font = Font(name='Arial', bold=True, size=14)
    ws.merge_cells('A2:H2')
    ws['A2'] = 'Rellena esta plantilla y sube el archivo en la evaluación correspondiente.'
    ws['A2'].font = Font(name='Arial', size=10, color='64748B')

    # Instrucciones
    ws.merge_cells('A3:H3')
    ws['A3'] = (
        'Probabilidad: 1=Baja, 2=Media, 3=Alta  |  '
        'Severidad: 1=Baja, 2=Media, 3=Alta'
    )
    ws['A3'].font = Font(name='Arial', size=9, italic=True, color='64748B')
    ws.row_dimensions[4].height = 6

    # Cabeceras
    header_font = Font(name='Arial', bold=True, size=11, color='FFFFFF')
    header_fill = PatternFill(start_color='0F172A', end_color='0F172A', fill_type='solid')
    header_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin'),
    )

    for col_num, header in enumerate(ENCabezado_EXCEL, 1):
        cell = ws.cell(row=5, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # Fila de ejemplo
    ejemplo = [
        'Soldador',
        'Ruido',
        'Ruido continuo en zona de soldadura',
        'Sordera',
        'Tapones auditivos',
        3,
        2,
        'Instalar cabinas de soldadura con insonorización',
    ]
    for col_num, value in enumerate(ejemplo, 1):
        cell = ws.cell(row=6, column=col_num, value=value)
        cell.border = thin_border
        cell.font = Font(name='Arial', size=10, color='94A3B8')

    # Columnas
    col_widths = [25, 25, 40, 30, 35, 15, 15, 35]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = FileResponse(
        buffer,
        as_attachment=True,
        filename='plantilla_evaluacion_riesgos.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    return response
