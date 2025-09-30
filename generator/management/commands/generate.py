import os
from .create import generate_create
from .delete import generate_delete
from .view import generate_views
from django.core.management.base import BaseCommand
from django.apps import apps



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            type=str,
            help='O nome da app a ser inspecionada.'
        )

    def handle(self, *args, **options):
        app_label = options['app_label']

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            self.stderr.write(self.style.ERROR(f"App '{app_label}' não encontrada."))
            return

        create_code = generate_create(app_label)
        delete_code = generate_delete(app_label)
        view_code = generate_views(app_label)

        imports_header = (
            "import json\n"
            "from django.http import JsonResponse\n"
            "from django.views.decorators.csrf import csrf_exempt\n"
            "from django.shortcuts import get_object_or_404\n"
            "from django.template.loader import render_to_string\n"
            f"from .models import {', '.join([m.__name__ for m in apps.get_app_config(app_label).get_models()])}\n\n"
        )

        final_code = (
                "# --- Código gerado automaticamente ---\n\n"
                + imports_header
                + create_code
                + "\n\n"
                + delete_code
                + "\n\n"
                + view_code
        )

        self.stdout.write(final_code)

        views_file_path = os.path.join(app_config.path, 'views.py')

        try:
            with open(views_file_path, 'a', encoding='utf-8') as f:
                f.write(final_code)

        except IOError as erro:
            self.stderr.write(self.style.ERROR(f"Não foi possível escrever no arquivo: {erro}"))