from django.apps import apps

FORM_TEMPLATE = """
class {form_name}(forms.ModelForm):
    class Meta:
        model = {model_name}
        fields = {fields_list}
"""

def generate_form_classes(app_label: str) -> str:

    app_config = apps.get_app_config(app_label)
    models = list(app_config.get_models())

    all_forms_code = []
    for model in models:
        editable_fields = [
            f.name for f in model._meta.get_fields()
            if not f.primary_key and not getattr(f, 'auto_now_add', False) and not getattr(f, 'auto_now', False)
        ]

        context = {
            'form_name': f"{model.__name__}Form",
            'model_name': model.__name__,
            'fields_list': f"['{ "', '".join(editable_fields)}']",
        }

        form_code = FORM_TEMPLATE.format(**context)
        all_forms_code.append(form_code)

    return "\n\n\n".join(all_forms_code)

