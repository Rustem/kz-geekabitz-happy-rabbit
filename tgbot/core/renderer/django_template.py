from django.template.loader import render_to_string


class DjangoTemplateRenderer:

    def render(self, template, **template_vars):
        return render_to_string(template, context=template_vars)