import os
from django.core.management.base import BaseCommand
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


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('app_label', type=str, help='O nome da app a ser inspecionada.')

    def handle(self, *args, **options):
        app_label = options['app_label']

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            self.stderr.write(self.style.ERROR(f"App '{app_label}' not found."))
            return

        models = list(app_config.get_models())

        if not models:
            self.stdout.write(self.style.WARNING(f"No models found in app '{app_label}'."))
            return

        all_views_code = []
        models_names = [model.__name__ for model in models]

        for model in models:
            editable_fields = [
                f.name for f in model._meta.get_fields()
                if not f.primary_key and not getattr(f, 'auto_now_add', False) and not getattr(f, 'auto_now', False)
            ]

            assignments_lines = []
            for field in editable_fields:
                assignments_lines.append(f"{field} = data.get('{field}')")
            field_assignments_str = ('\n' + ' ' * 8).join(assignments_lines)

            creation_args_lines = []
            for field in editable_fields:
                creation_args_lines.append(f"new_instance.{field}={field},")
            model_creation_args_str = ('\n' + ' ' * 12).join(creation_args_lines)

            context = {
                'model_name': model.__name__,
                'model_name_lower': model.__name__.lower(),
                'field_assignments': field_assignments_str,
                'model_creation_args': model_creation_args_str,
            }

            view_code = API_VIEW_TEMPLATE.format(**context)
            all_views_code.append(view_code)

        self.stdout.write(self.style.WARNING("\n--- PONTO DE VERIFICAÇÃO ANTES DO LOOP ---"))
        self.stdout.write(f"Conteúdo da lista 'models': {models}")
        self.stdout.write(f"Conteúdo da lista 'models_names': {models_names}")
        self.stdout.write(self.style.WARNING("----------------------------------------\n"))

        imports_header = "import json\n"
        imports_header += "from django.http import JsonResponse\n"
        imports_header += "from django.views.decorators.csrf import csrf_exempt\n"
        imports_header += f"from .models import {', '.join([model.__name__ for model in models])}\n\n"

        final_code = imports_header + "\n".join(all_views_code)

        views_file_path = os.path.join(app_config.path, 'views.py')

        try:
            # Abre o arquivo em modo append ('a')
            with open(views_file_path, 'a', encoding='utf-8') as f:
                f.write('\n\n# --- Código gerado automaticamente ---\n')
                f.write(final_code)

            self.stdout.write(
                self.style.SUCCESS(f"Código gerado e adicionado com sucesso ao final de '{views_file_path}'"))

        except IOError as erro:
            self.stderr.write(self.style.ERROR(f"Não foi possível escrever no arquivo: {erro}"))