from django.apps import apps

VIEW_TEMPLATE = """
@csrf_exempt  # remova em produção (ideal: nem usar)
@login_required
@require_POST
def {model_name_lower}_update(request, pk):

    obj = get_object_or_404({model_name}, pk=pk)

    form = {form_name}(request.POST,request.FILES, instance=obj)

    if form.is_valid():
        form.save()
        messages.success(request, "{model_name} atualizado com sucesso!")
    else:
        messages.error(request, "Verifique os erros no formulário.")

    return redirect("{model_name_lower}_list")
"""

def generate_form_update(app_label: str) -> str:
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
            'form_name': f"{model.__name__}Form",
        }

        view_code = VIEW_TEMPLATE.format(**context)
        all_views_code.append(view_code)

    return "\n\n".join(all_views_code)



