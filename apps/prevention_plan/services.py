def get_plan_estadisticas(plan):
    if not plan:
        return {
            'total': 7, 'completados': 0, 'pendientes': 7,
            'no_aplica': 0, 'progreso': 0,
        }

    estados = [
        plan.politica_estado,
        plan.organigrama_estado,
        plan.delegado_estado,
        plan.recurso_estado,
        plan.funciones_estado,
        plan.ett_estado,
        plan.teletrabajo_estado,
    ]

    return {
        'total': 7,
        'completados': sum(1 for e in estados if e == 'completo'),
        'pendientes': sum(1 for e in estados if e == 'pendiente'),
        'no_aplica': sum(1 for e in estados if e == 'no_aplica'),
        'progreso': plan.progreso_total,
    }
