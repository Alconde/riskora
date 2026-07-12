"""
Servicios de cálculo de riesgo — Matriz INSST.

  Grado de Riesgo (GR) = Probabilidad × Severidad

  Probabilidad: 1=Baja, 2=Media, 3=Alta
  Severidad:    1=Baja, 2=Media, 3=Alta

  Escala de niveles (1-9):
    1-2 = Muy bajo
    3-4 = Bajo
    5-6 = Medio
    7-8 = Alto
    9   = Muy alto
"""


# Matriz INSST: [probabilidad][severidad] → grado de riesgo (1-9)
MATRIZ_INSST = [
    [1, 2, 3],   # Probabilidad Baja:   B×B=1, B×M=2, B×A=3
    [2, 4, 6],   # Probabilidad Media:  M×B=2, M×M=4, M×A=6
    [3, 6, 9],   # Probabilidad Alta:   A×B=3, A×M=6, A×A=9
]

# Probabilidad
ETIQUETAS_PROBABILIDAD = {
    1: 'Baja',
    2: 'Media',
    3: 'Alta',
}

# Severidad
ETIQUETAS_SEVERIDAD = {
    1: 'Baja',
    2: 'Media',
    3: 'Alta',
}

# Niveles de riesgo según el grado (1-9)
NIVELES_RIESGO = {
    1: {
        'grado': 1,
        'nivel': 'muy_bajo',
        'etiqueta': 'Muy bajo',
        'color': '#22c55e',
        'color_fondo': '#dcfce7',
        'color_texto': '#15803d',
        'descripcion': 'No requiere acción preventiva específica.',
        'badge_class': 'badge-muy_bajo',
    },
    2: {
        'grado': 2,
        'nivel': 'muy_bajo',
        'etiqueta': 'Muy bajo',
        'color': '#22c55e',
        'color_fondo': '#dcfce7',
        'color_texto': '#15803d',
        'descripcion': 'No requiere acción preventiva específica.',
        'badge_class': 'badge-muy_bajo',
    },
    3: {
        'grado': 3,
        'nivel': 'bajo',
        'etiqueta': 'Bajo',
        'color': '#84cc16',
        'color_fondo': '#ecfccb',
        'color_texto': '#3f6212',
        'descripcion': 'No necesita mejora inmediata. Soluciones de bajo costo.',
        'badge_class': 'badge-bajo',
    },
    4: {
        'grado': 4,
        'nivel': 'bajo',
        'etiqueta': 'Bajo',
        'color': '#84cc16',
        'color_fondo': '#ecfccb',
        'color_texto': '#3f6212',
        'descripcion': 'No necesita mejora inmediata. Soluciones de bajo costo.',
        'badge_class': 'badge-bajo',
    },
    5: {
        'grado': 5,
        'nivel': 'medio',
        'etiqueta': 'Medio',
        'color': '#eab308',
        'color_fondo': '#fef9c3',
        'color_texto': '#a16207',
        'descripcion': 'Deben hacerse esfuerzos para reducir el riesgo.',
        'badge_class': 'badge-medio',
    },
    6: {
        'grado': 6,
        'nivel': 'medio',
        'etiqueta': 'Medio',
        'color': '#eab308',
        'color_fondo': '#fef9c3',
        'color_texto': '#a16207',
        'descripcion': 'Deben hacerse esfuerzos para reducir el riesgo.',
        'badge_class': 'badge-medio',
    },
    7: {
        'grado': 7,
        'nivel': 'alto',
        'etiqueta': 'Alto',
        'color': '#f97316',
        'color_fondo': '#ffedd5',
        'color_texto': '#c2410c',
        'descripcion': 'No debe comenzarse el trabajo hasta reducir el riesgo.',
        'badge_class': 'badge-alto',
    },
    8: {
        'grado': 8,
        'nivel': 'alto',
        'etiqueta': 'Alto',
        'color': '#f97316',
        'color_fondo': '#ffedd5',
        'color_texto': '#c2410c',
        'descripcion': 'No debe comenzarse el trabajo hasta reducir el riesgo.',
        'badge_class': 'badge-alto',
    },
    9: {
        'grado': 9,
        'nivel': 'muy_alto',
        'etiqueta': 'Muy alto',
        'color': '#ef4444',
        'color_fondo': '#fee2e2',
        'color_texto': '#b91c1c',
        'descripcion': 'No se permite el trabajo hasta eliminar o controlar el riesgo.',
        'badge_class': 'badge-muy_alto',
    },
}


def calcular_grado_riesgo(probabilidad: int, severidad: int) -> dict:
    """
    Calcula el grado de riesgo según la matriz INSST.

    GR = Probabilidad × Severidad
    """
    if not (1 <= probabilidad <= 3 and 1 <= severidad <= 3):
        raise ValueError(
            f'Valores fuera de rango: probabilidad={probabilidad}, severidad={severidad}. '
            'Ambos deben estar entre 1 y 3.'
        )

    grado = MATRIZ_INSST[probabilidad - 1][severidad - 1]
    return NIVELES_RIESGO[grado]


def obtener_etiqueta_probabilidad(valor: int) -> str:
    """Devuelve la etiqueta legible de la probabilidad."""
    return ETIQUETAS_PROBABILIDAD.get(valor, 'Desconocida')


def obtener_etiqueta_severidad(valor: int) -> str:
    """Devuelve la etiqueta legible de la severidad."""
    return ETIQUETAS_SEVERIDAD.get(valor, 'Desconocida')


def calcular_estadisticas_evaluacion(items):
    """
    Calcula estadísticas resumen de una evaluación de riesgos.
    """
    stats = {
        'total': items.count(),
        'muy_bajo': items.filter(nivel_riesgo='muy_bajo').count(),
        'bajo': items.filter(nivel_riesgo='bajo').count(),
        'medio': items.filter(nivel_riesgo='medio').count(),
        'alto': items.filter(nivel_riesgo='alto').count(),
        'muy_alto': items.filter(nivel_riesgo='muy_alto').count(),
    }
    stats['requieren_accion'] = (
        stats['medio'] + stats['alto'] + stats['muy_alto']
    )
    return stats


def es_nivel_requiere_accion(nivel: str) -> bool:
    """Indica si un nivel de riesgo requiere acción preventiva."""
    return nivel in ('medio', 'alto', 'muy_alto')
