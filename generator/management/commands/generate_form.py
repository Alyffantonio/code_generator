import os
from django.core.management.base import BaseCommand
from django.apps import apps

from .form.details_form import generate_form_details
from .form.post_form import generate_form_classes
from .form.create_form import  generate_form_view
from .form.read_form import generate_form_read
from .form.update_form import  generate_form_update
from .form.delete_form import  generate_form_delete
from .form.imports import generate_imports, generate_form_imports
from .urls.create_urls import create_urls

class Command(BaseCommand):
    help = "Gera o arquivo forms.py ou views.py para uma app."

    def add_arguments(self, parser):
        parser.add_argument('app_label', type=str, help='O nome da app a ser inspecionada.')

    def handle(self, *args, **options):
        app_label = options['app_label']

        create_urls(app_label, overwrite=options.get('overwrite_urls', False), builder="form")

        self._generate_form_file(app_label)

        self._generate_view_file(app_label)

    def _generate_form_file(self, app_label):
        self.stdout.write(self.style.SUCCESS(f"Iniciando geração do forms.py para a app '{app_label}'..."))
        try:
            app_config = apps.get_app_config(app_label)

            imports_code = generate_form_imports(app_label)
            forms_code = generate_form_classes(app_label)
            final_code = f"{imports_code}\n\n{forms_code}"

            forms_file_path = os.path.join(app_config.path, 'forms.py')

            if os.path.exists(forms_file_path):
                self.stdout.write(self.style.WARNING(f"Arquivo '{forms_file_path}' já existe. Exibindo no console."))
                self.stdout.write(final_code)
            else:
                with open(forms_file_path, 'w', encoding='utf-8') as f:
                    f.write(final_code)
                self.stdout.write(self.style.SUCCESS(f"Arquivo '{forms_file_path}' criado com sucesso!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro: {e}"))

    def _generate_view_file(self, app_label):
        self.stdout.write(self.style.SUCCESS(f"Iniciando geração do views.py para a app '{app_label}'..."))
        try:
            app_config = apps.get_app_config(app_label)

            imports_code = generate_imports(app_label)
            views_code_create = generate_form_view(app_label)
            views_code_update = generate_form_update(app_label)
            views_code_delete = generate_form_delete(app_label)
            views_code_read = generate_form_read(app_label)
            views_code_details = generate_form_details(app_label)

            final_code = f"{imports_code}\n\n{views_code_read}\n\n{views_code_details}\n\n{views_code_create}\n\n{views_code_update}\n\n{views_code_delete}"

            views_file_path = os.path.join(app_config.path, 'views.py')
            with open(views_file_path, 'a', encoding='utf-8') as f:
                f.write("\n\n# --- Código Gerado Automaticamente ---\n")
                f.write(final_code)
            self.stdout.write(self.style.SUCCESS(f"Código adicionado com sucesso em '{views_file_path}'"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro: {e}"))