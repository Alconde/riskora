from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render


@login_required(login_url='/login/')
def busqueda_global(request):
    q = request.GET.get('q', '').strip()
    empresa = getattr(request, 'active_company', None)
    resultados = []

    if len(q) < 2:
        return render(request, 'core/search.html', {'q': q, 'resultados': resultados, 'total': 0})

    q_lower = q.lower()

    def match(text):
        return q_lower in text.lower() if text else False

    # Trabajadores
    from apps.workers.models import Worker
    workers = Worker.objects.select_related('company', 'work_center', 'job_position')
    if empresa:
        workers = workers.filter(company=empresa)
    else:
        workers = workers.none()
    for w in workers:
        searchable = f'{w.first_name} {w.last_name} {w.national_id or ""} {w.email or ""} {w.employee_code or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Trabajador',
                'titulo': f'{w.first_name} {w.last_name}',
                'subtitulo': f'{w.job_position or "-"} · {w.work_center or "-"}',
                'url': f'/trabajadores/{w.pk}/',
                'badge': 'badge-info',
            })

    # Documentos
    from apps.documents.models import Document
    docs = Document.objects.select_related('company', 'category')
    if empresa:
        docs = docs.filter(company=empresa)
    else:
        docs = docs.none()
    for d in docs:
        searchable = f'{d.title} {d.code or ""} {d.description or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Documento',
                'titulo': d.title,
                'subtitulo': f'{d.category} · {d.get_status_display()}',
                'url': f'/documents/{d.id}/',
                'badge': 'badge-success' if d.status == 'valid' else 'badge-danger',
            })

    # Evaluaciones de riesgos
    from apps.risk_assessment.models import EvaluacionRiesgos
    evals = EvaluacionRiesgos.objects.select_related('empresa', 'centro_trabajo')
    if empresa:
        evals = evals.filter(empresa=empresa)
    else:
        evals = evals.none()
    for e in evals:
        searchable = f'{e.titulo} {e.centro_trabajo or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Evaluacion de Riesgos',
                'titulo': e.titulo,
                'subtitulo': f'{e.centro_trabajo or "-"} · {e.get_estado_display()}',
                'url': f'/evaluaciones/{e.pk}/',
                'badge': 'badge-success' if e.estado == 'aprobada' else 'badge-warning',
            })

    # No conformidades
    from apps.corrective_actions.models import NoConformidad
    ncs = NoConformidad.objects.select_related('empresa', 'centro_trabajo')
    if empresa:
        ncs = ncs.filter(empresa=empresa)
    else:
        ncs = ncs.none()
    for nc in ncs:
        searchable = f'{nc.codigo} {nc.titulo} {nc.descripcion[:100] or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'No Conformidad',
                'titulo': f'{nc.codigo} - {nc.titulo}',
                'subtitulo': f'{nc.get_fuente_display()} · {nc.get_estado_display()}',
                'url': f'/nc/{nc.pk}/',
                'badge': 'badge-danger' if nc.estado in ('abierta', 'en_investigacion') else 'badge-success',
            })

    # Formacion
    from apps.training.models import TrainingRecord
    records = TrainingRecord.objects.select_related('company', 'worker', 'course')
    if empresa:
        records = records.filter(company=empresa)
    else:
        records = records.none()
    for r in records:
        searchable = f'{r.worker} {r.course} {r.certificate_number or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Formacion',
                'titulo': f'{r.worker} - {r.course}',
                'subtitulo': f'{r.get_status_display()} · Cert: {r.certificate_number or "-"}',
                'url': f'/training/records/{r.pk}/',
                'badge': 'badge-success' if r.status == 'completed' else 'badge-warning',
            })

    # Accidentes
    from apps.incidents.models import Accidente
    accs = Accidente.objects.select_related('empresa', 'centro_trabajo')
    if empresa:
        accs = accs.filter(empresa=empresa)
    else:
        accs = accs.none()
    for a in accs:
        searchable = f'{a.codigo} {a.titulo} {a.ubicacion or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Accidente',
                'titulo': f'{a.codigo} - {a.titulo}',
                'subtitulo': f'{a.get_tipo_display()} · {a.get_estado_display()}',
                'url': f'/seguridad/accidentes/{a.pk}/',
                'badge': 'badge-danger' if a.estado == 'abierto' else 'badge-success',
            })

    # Autorizaciones
    from apps.authorizations.models import AutorizacionTrabajador, RequisitoAutorizacion
    auths = AutorizacionTrabajador.objects.select_related('trabajador', 'requisito', 'empresa')
    if empresa:
        auths = auths.filter(empresa=empresa)
    else:
        auths = auths.none()
    for au in auths:
        searchable = f'{au.trabajador} {au.requisito} {au.numero_certificado or ""} {au.entidad_emisora or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Autorizacion',
                'titulo': f'{au.trabajador} - {au.requisito}',
                'subtitulo': f'{au.get_estado_display()} · Cert: {au.numero_certificado or "-"}',
                'url': f'/autorizaciones/trabajador/{au.trabajador_id}/',
                'badge': 'badge-success' if au.estado == 'activa' else 'badge-danger',
            })

    # Tareas
    from apps.tasks.models import Task
    tasks = Task.objects.select_related('company', 'assigned_to')
    if empresa:
        tasks = tasks.filter(company=empresa)
    else:
        tasks = tasks.none()
    for t in tasks:
        searchable = f'{t.title} {t.description or ""}'
        if match(searchable):
            resultados.append({
                'tipo': 'Tarea',
                'titulo': t.title,
                'subtitulo': f'{t.get_priority_display()} · {t.get_status_display()}',
                'url': f'/tareas/{t.pk}/',
                'badge': 'badge-danger' if t.priority == 'critical' else 'badge-warning',
            })

    return render(request, 'core/search.html', {
        'q': q,
        'resultados': resultados,
        'total': len(resultados),
    })
