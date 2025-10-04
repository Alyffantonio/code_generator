from django.apps import apps

API_VIEW_TEMPLATE = """
@csrf_exempt
def {model_name_lower}_view_api(request):
    if request.method != 'GET':
        return JsonResponse({{'error': 'Método não permitido, use GET'}}, status=405)

    try:
        list_view = {model_name}.objects.all()
        
        # ajuste o caminho do template abaixo:
        html = render_to_string('template/list.html', {{'list_view': list_view}}, request=request)
        
        return JsonResponse({{'html': html}}, status=200)
        
    except Exception as e:
        return JsonResponse({{'error': f'Ocorreu um erro: {{str(e)}}'}}, status=500)
"""



def generate_views(app_label: str) -> str:
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

