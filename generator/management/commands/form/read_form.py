from django.apps import apps

VIEW_TEMPLATE = """
@csrf_exempt  # remova em produção (ideal: nem usar)
@login_required
@require_GET
def {model_name_lower}_read(request):

    objs = {model_name}.objects.all()
    
    context = {{"objects_list": objs}}
    
    return render(request, "{app_label}/{model_name_lower}_read.html", context)
"""


def generate_form_read(app_label: str) -> str:
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        return f"# ERRO: App '{app_label}' não encontrada."

    models = list(app_config.get_models())
    if not models:
        return f"# AVISO: Nenhum modelo encontrado na app '{app_label}'."

    all_views_code = []

    for model in models:
        context = {
            'app_label': app_label,
            'model_name': model.__name__,
            'model_name_lower': model.__name__.lower(),
        }

        view_code = VIEW_TEMPLATE.format(**context)
        all_views_code.append(view_code)

    return "\n\n".join(all_views_code)



