from django.apps import apps

API_VIEW_TEMPLATE = """
@csrf_exempt
def {model_name_lower}_create_api(request):
    if request.method != 'POST':
        return JsonResponse({{'error': 'Método não permitido, use POST'}}, status=405)

    try:
        data = json.loads(request.body)

        {field_assignments}

        new_instance = {model_name}(
            {model_creation_args}
        )
        new_instance.save()

        response_data = {{
            'message': '{model_name} criado com sucesso!',
            'data': {{ 'id': new_instance.id }}
        }}
        return JsonResponse(response_data, status=201)

    except Exception as e:
        return JsonResponse({{'error': f'Ocorreu um erro: {{str(e)}}'}}, status=500)
"""


def generate_create(app_label: str) -> str:
    app_config = apps.get_app_config(app_label)
    models = list(app_config.get_models())

    all_views_code = []
    for model in models:
        editable_fields = [
            f.name for f in model._meta.get_fields()
            if not f.primary_key and not getattr(f, 'auto_now_add', False) and not getattr(f, 'auto_now', False)
        ]

        assignments_lines = [f"{field} = data.get('{field}')" for field in editable_fields]
        field_assignments_str = ('\n' + ' ' * 8).join(assignments_lines)

        creation_args_lines = [f"{field}={field}," for field in editable_fields]
        model_creation_args_str = ('\n' + ' ' * 12).join(creation_args_lines)

        context = {
            'model_name': model.__name__,
            'model_name_lower': model.__name__.lower(),
            'field_assignments': field_assignments_str,
            'model_creation_args': model_creation_args_str,
        }

        view_code = API_VIEW_TEMPLATE.format(**context)
        all_views_code.append(view_code)

    return "\n".join(all_views_code)

