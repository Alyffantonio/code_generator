from django.apps import apps

API_VIEW_TEMPLATE = """
@csrf_exempt
def {model_name_lower}_delete_api(request, id_object):
    if request.method != 'DELETE':
        return JsonResponse({{'error': 'Método não permitido, use DELETE'}}, status=405)

    try:
        instance = get_object_or_404({model_name}, id=id_object)

        instance.delete()

        return JsonResponse(
            {{'message': 'Objeto excluído com sucesso', 'data': {{'id': id_object}}}},
            status=200
        )

    except Exception as e:
        return JsonResponse({{'error': f'Ocorreu um erro: {{str(e)}}'}}, status=500)
"""


def generate_delete(app_label: str) -> str:
    app_config = apps.get_app_config(app_label)
    models = list(app_config.get_models())

    all_views_code = []
    for model in models:
        context = {
            'model_name': model.__name__,
            'model_name_lower': model.__name__.lower(),
        }
        view_code = API_VIEW_TEMPLATE.format(**context)
        all_views_code.append(view_code)

    return "\n".join(all_views_code)

