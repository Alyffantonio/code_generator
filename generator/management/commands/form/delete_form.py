from django.apps import apps

VIEW_TEMPLATE = """
@csrf_exempt  # remova em produção (ideal: nem usar)
@login_required
@require_POST
def {model_name_lower}_delete(request, pk):

    obj = get_object_or_404({model_name}, pk=pk)
    
    try:
        obj.delete()
    except ProtectedError:
        messages.error(request, "Não foi possível excluir: existe(m) registro(s) relacionado(s).")
    except (IntegrityError, DatabaseError) as e:
        messages.error(request, f"Erro de banco ao excluir: {{e}}")
    else:
        messages.success(request, f"Registro excluído com sucesso!")
        
    return redirect("{model_name_lower}_list")
"""

def generate_form_delete(app_label: str) -> str:
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



