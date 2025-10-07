from django.apps import apps


VIEW_TEMPLATE = """
@login_required
@require_http_methods(["GET", "POST"])
def {model_name_lower}_details(request, id):

    if request.method == "GET":
        
        objects = get_object_or_404({model_name}, id=id)

        context = {{
            "objects_details": objects,
        }}

    return render(request, "{app_label}/{model_name_lower}_read.html", context)
"""


def generate_form_details(app_label: str)->str:
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
            'model_name':model.__name__,
            'model_name_lower':model.__name__.lower(),
        }

        view_code = VIEW_TEMPLATE.format(**context)
        all_views_code.append(view_code)

    return "\n\n".join(all_views_code)