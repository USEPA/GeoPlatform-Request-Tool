from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def signature_line(context):
    portal = context['PORTAL']
    signature_line_template = template.Template(portal.email_signature_content)
    return signature_line_template.render(context)
