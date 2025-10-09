from django.db import models

API_VIEW_TEMPLATE = """
@csrf_exempt
def {model_name_lower}_create_api(request):
    if request.method != 'POST':
        return JsonResponse({{'error': 'Método não permitido, use POST'}}, status=405)
    try:
        try:
            data = json.loads(request.body.decode('utf-8') or '{{}}')
        except json.JSONDecodeError:
            return JsonResponse({{'error': 'JSON inválido'}}, status=400)

        {field_assignments}

        new_instance = {model_name}(
            {model_creation_args}
        )
        new_instance.save()

        response_data = {{
            'message': '{model_name} criado com sucesso!',
            'data': {{ 'id': new_instance.pk }}
        }}
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({{'error': f'Ocorreu um erro: {{str(e)}}'}}, status=500)
"""

def generate_create(model):

    editable_fields = [
        f for f in model._meta.fields
        if not f.primary_key
        and not getattr(f, "auto_now", False)
        and not getattr(f, "auto_now_add", False)
    ]

    assignment_lines = []
    creation_arg_lines = []

    for f in editable_fields:
        name = f.name
        if isinstance(f, models.ForeignKey):
            assignment_lines.append(f"{name}_id = data.get('{name}_id')")
            creation_arg_lines.append(f"{name}_id={name}_id,")
        else:
            assignment_lines.append(f"{name} = data.get('{name}')")
            creation_arg_lines.append(f"{name}={name},")

    field_assignments_str = ('\n' + ' ' * 8).join(assignment_lines) if assignment_lines else "pass"
    model_creation_args_str = ('\n' + ' ' * 12).join(creation_arg_lines) if creation_arg_lines else ""

    context = {
        "model_name": model.__name__,
        "model_name_lower": model._meta.model_name,
        "field_assignments": field_assignments_str,
        "model_creation_args": model_creation_args_str,
    }
    return API_VIEW_TEMPLATE.format(**context)
