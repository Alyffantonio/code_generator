import os
from generator.management.commands.api.post import generate_create
from generator.management.commands.api.delete import generate_delete
from generator.management.commands.api.get import generate_views
from generator.management.commands.api.put import generate_put
from generator.management.commands.api.patch import generate_patch
from generator.management.commands.urls import create_urls
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

        create_urls(app_label, overwrite=options.get('overwrite_urls', False))

        create_code = generate_create(app_label)
        delete_code = generate_delete(app_label)
        view_code = generate_views(app_label)
        put_code = generate_put(app_label)
        patch_code = generate_patch(app_label)

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
                + "\n"
                + delete_code
                + "\n"
                + view_code
                + "\n"
                + put_code
                + "\n"
                + patch_code
        )

        self.stdout.write(final_code)

        views_file_path = os.path.join(app_config.path, 'views.py')

        try:
            with open(views_file_path, 'a', encoding='utf-8') as f:
                f.write(final_code)

        except IOError as erro:
            self.stderr.write(self.style.ERROR(f"Não foi possível escrever no arquivo: {erro}"))