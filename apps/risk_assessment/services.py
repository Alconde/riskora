"""
Servicios de cálculo de riesgo según metodología INSST.

Matriz de Evaluación de Riesgos del INSST:
  Probabilidad (3 niveles) × Severidad (3 niveles) = Grado de Riesgo

  Niveles de actuación:
    1 = Trivial       → No requiere acción preventiva
    2 = Tolerable     → No necesita mejora inmediata
    3 = Moderado      → Deben hacerse esfuerzos para reducir
    4 = Importante    → No comenzar hasta reducir el riesgo
    5 = Intolerable   → No se permite el trabajo
"""


# Matriz INSST: [probabilidad][severidad] → grado de riesgo (1-5)
# Índices: 0=Baja/1=Media/2=Alta (prob)
#          0=Ligeramente/1=Dañino/2=Extremadamente (sev)
MATRIZ_INSST = [
    [1, 2, 3],   # Probabilidad Baja
    [2, 3, 4],   # Probabilidad Media
    [3, 4, 5],   # Probabilidad Alta
]

# Probabilidad: valor numérico → etiqueta
ETIQUETAS_PROBABILIDAD = {
    1: 'Baja',
    2: 'Media',
    3: 'Alta',
}

# Severidad: valor numérico → etiqueta
ETIQUETAS_SEVERIDAD = {
    1: 'Ligeramente dañino',
    2: 'Dañino',
    3: 'Extremadamente dañino',
}

# Grado de riesgo: valor numérico → datos completos
NIVELES_RIESGO = {
    1: {
        'grado': 1,
        'nivel': 'trivial',
        'etiqueta': 'Trivial',
        'color': '#22c55e',
        'color_fondo': '#dcfce7',
        'color_texto': '#15803d',
        'descripcion': 'No requiere acción preventiva.',
        'badge_class': 'badge-success',
    },
    2: {
        'grado': 2,
        'nivel': 'tolerable',
        'etiqueta': 'Tolerable',
        'color': '#84cc16',
        'color_fondo': '#ecfccb',
        'color_texto': '#3f6212',
        'descripcion': 'No necesita mejora inmediata, pero requiere soluciones de bajo costo o menos urgentes.',
        'badge_class': 'badge-tolerable',
    },
    3: {
        'grado': 3,
        'nivel': 'moderado',
        'etiqueta': 'Moderado',
        'color': '#eab308',
        'color_fondo': '#fef9c3',
        'color_texto': '#a16207',
        'descripcion': 'Deben hacerse esfuerzos para reducir el riesgo.',
        'badge_class': 'badge-moderate',
    },
    4: {
        'grado': 4,
        'nivel': 'importante',
        'etiqueta': 'Importante',
        'color': '#f97316',
        'color_fondo': '#ffedd5',
        'color_texto': '#c2410c',
        'descripcion': 'No debe comenzarse el trabajo hasta reducir el riesgo.',
        'badge_class': 'badge-important',
    },
    5: {
        'grado': 5,
        'nivel': 'intolerable',
        'etiqueta': 'Intolerable',
        'color': '#ef4444',
        'color_fondo': '#fee2e2',
        'color_texto': '#b91c1c',
        'descripcion': 'No se permite el trabajo hasta eliminar o controlar el riesgo.',
        'badge_class': 'badge-intolerable',
    },
}


def calcular_grado_riesgo(probabilidad: int, severidad: int) -> dict:
    """
    Calcula el grado de riesgo según la matriz INSST.

    Args:
        probabilidad: 1=Baja, 2=Media, 3=Alta
        severidad: 1=Ligeramente dañino, 2=Dañino, 3=Extremadamente dañino

    Returns:
        dict con grado, nivel, etiqueta, color, descripcion, badge_class
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

    Args:
        items: QuerySet de RiskAssessmentItem

    Returns:
        dict con contadores por nivel y totales
    """
    stats = {
        'total': items.count(),
        'trivial': items.filter(nivel_riesgo='trivial').count(),
        'tolerable': items.filter(nivel_riesgo='tolerable').count(),
        'moderado': items.filter(nivel_riesgo='moderado').count(),
        'importante': items.filter(nivel_riesgo='importante').count(),
        'intolerable': items.filter(nivel_riesgo='intolerable').count(),
    }
    stats['requieren_accion'] = (
        stats['moderado'] + stats['importante'] + stats['intolerable']
    )
    return stats


def es_nivel_requiere_accion(nivel: str) -> bool:
    """Indica si un nivel de riesgo requiere acción preventiva."""
    return nivel in ('moderado', 'importante', 'intolerable')
