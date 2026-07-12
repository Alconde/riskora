from django import template
from apps.risk_assessment.services import NIVELES_RIESGO

register = template.Library()


@register.filter
def badge_riesgo(nivel):
    """Devuelve la clase CSS del badge según el nivel de riesgo."""
    niveles = {
        'muy_bajo': 'badge-muy_bajo',
        'bajo': 'badge-bajo',
        'medio': 'badge-medio',
        'alto': 'badge-alto',
        'muy_alto': 'badge-muy_alto',
    }
    return niveles.get(nivel, 'badge-secondary')


@register.filter
def color_riesgo(nivel):
    """Devuelve el color hex del nivel de riesgo."""
    niveles = {
        'muy_bajo': '#22c55e',
        'bajo': '#84cc16',
        'medio': '#eab308',
        'alto': '#f97316',
        'muy_alto': '#ef4444',
    }
    return niveles.get(nivel, '#6b7280')


@register.filter
def color_fondo_riesgo(nivel):
    """Devuelve el color de fondo del nivel de riesgo."""
    niveles = {
        'muy_bajo': '#dcfce7',
        'bajo': '#ecfccb',
        'medio': '#fef9c3',
        'alto': '#ffedd5',
        'muy_alto': '#fee2e2',
    }
    return niveles.get(nivel, '#f3f4f6')


@register.filter
def color_texto_riesgo(nivel):
    """Devuelve el color de texto del nivel de riesgo."""
    niveles = {
        'muy_bajo': '#15803d',
        'bajo': '#3f6212',
        'medio': '#a16207',
        'alto': '#c2410c',
        'muy_alto': '#b91c1c',
    }
    return niveles.get(nivel, '#374151')


@register.filter
def etiqueta_riesgo(nivel):
    """Devuelve la etiqueta legible del nivel de riesgo."""
    datos = NIVELES_RIESGO.values()
    for v in datos:
        if v['nivel'] == nivel:
            return v['etiqueta']
    return nivel


@register.filter
def descripcion_riesgo(nivel):
    """Devuelve la descripción del nivel de riesgo."""
    datos = NIVELES_RIESGO.values()
    for v in datos:
        if v['nivel'] == nivel:
            return v['descripcion']
    return ''


@register.filter
def risk_item_style(nivel):
    """Devuelve CSS inline completo para un item de riesgo."""
    color = color_riesgo(nivel)
    return f'border-left: 4px solid {color};'
