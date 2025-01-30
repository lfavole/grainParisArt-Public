from django import template

register = template.Library()


@register.filter
def format_runtime(value):
    """Format a film runtime in minutes into a human-readable string."""
    hours = value // 60
    minutes = value % 60
    return f"{hours}h{minutes:02d}"
