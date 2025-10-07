from django.apps import apps

VIEW_TEMPLATE = """
@csrf_exempt
@require_http_methods(["GET", "POST"])
def {model_name_lower}_create(request):
    if request.method == 'POST':
        form = {form_name}(request.POST)
        if form.is_valid():
        
            # se precisar manipular antes de salvar:
            # obj = form.save(commit=False)
            # obj.algum_campo = "valor"
            # obj.save()
            form.save()
            
            messages.success(request, "Livro criado com sucesso!")
            return redirect('pagina_de_sucesso') # Lembre-se de criar essa URL e view
        
        else:
            messages.error(request, "Verifique os erros no formulário.")
    else:
        form = {form_name}()

    return render(request, '{app_label}/{model_name_lower}_form.html', {{'form': form}}) #altere de acordo com o seu arquivo html
"""


def generate_form_view(app_label: str) -> str:
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



