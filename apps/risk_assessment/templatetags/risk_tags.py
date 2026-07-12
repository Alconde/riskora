from django import template
from apps.risk_assessment.services import NIVELES_RIESGO

register = template.Library()


@register.filter
def badge_riesgo(nivel):
    """Devuelve la clase CSS del badge según el nivel de riesgo INSST."""
    niveles = {
        'trivial': 'badge-success',
        'tolerable': 'badge-tolerable',
        'moderado': 'badge-moderate',
        'importante': 'badge-important',
        'intolerable': 'badge-intolerable',
    }
    return niveles.get(nivel, 'badge-secondary')


@register.filter
def color_riesgo(nivel):
    """Devuelve el color hex del nivel de riesgo."""
    niveles = {
        'trivial': '#22c55e',
        'tolerable': '#84cc16',
        'moderado': '#eab308',
        'importante': '#f97316',
        'intolerable': '#ef4444',
    }
    return niveles.get(nivel, '#6b7280')


@register.filter
def color_fondo_riesgo(nivel):
    """Devuelve el color de fondo del nivel de riesgo."""
    niveles = {
        'trivial': '#dcfce7',
        'tolerable': '#ecfccb',
        'moderado': '#fef9c3',
        'importante': '#ffedd5',
        'intolerable': '#fee2e2',
    }
    return niveles.get(nivel, '#f3f4f6')


@register.filter
def color_texto_riesgo(nivel):
    """Devuelve el color de texto del nivel de riesgo."""
    niveles = {
        'trivial': '#15803d',
        'tolerable': '#3f6212',
        'moderado': '#a16207',
        'importante': '#c2410c',
        'intolerable': '#b91c1c',
    }
    return niveles.get(nivel, '#374151')


@register.filter
def etiqueta_riesgo(nivel):
    """Devuelve la etiqueta legible del nivel de riesgo."""
    datos = NIVELES_RIESGO.get(nivel, {})
    return datos.get('etiqueta', nivel)


@register.filter
def descripcion_riesgo(nivel):
    """Devuelve la descripción del nivel de riesgo."""
    datos = NIVELES_RIESGO.get(nivel, {})
    return datos.get('descripcion', '')


@register.filter
def risk_item_style(nivel):
    """Devuelve CSS inline completo para un item de riesgo."""
    datos = NIVELES_RIESGO.get(nivel, {})
    color = datos.get('color', '#6b7280')
    return f'border-left: 4px solid {color};'
