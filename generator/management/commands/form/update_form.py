from django.apps import apps

VIEW_TEMPLATE = """
@require_http_methods(["GET", "POST"])
def {model_name_lower}_update(request, id):
    obj = get_object_or_404({model_name}, id=id)

    if request.method == "POST":
        form = {form_name}(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, "{model_name} atualizado com sucesso!")
            # ajuste a rota conforme seu projeto (detail/list)
            return redirect("{app_label}:{model_name_lower}_detail", id=obj.id)
        else:
            messages.error(request, "Verifique os erros no formulário.")
    else:
        form = {form_name}(instance=obj)
    
    context = {{
        'form' : form,
        'object': obj
    }}
    
    return render(request, "{app_label}/{model_name_lower}_form.html", context )
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



