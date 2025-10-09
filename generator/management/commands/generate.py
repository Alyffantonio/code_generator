import os
from generator.management.commands.api.post import generate_create
from generator.management.commands.api.delete import generate_delete
from generator.management.commands.api.get import generate_views
from generator.management.commands.api.put import generate_put
from generator.management.commands.api.patch import generate_patch
from generator.management.commands.urls.create_urls import create_urls
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

        models = list(app_config.get_models())
        if not models:
            self.stderr.write(self.style.WARNING(f"Nenhum model encontrado em '{app_label}'."))
            return

        create_urls(app_label, overwrite=options.get('overwrite_urls', False), builder="api")

        model_names = ", ".join([m.__name__ for m in models])
        imports_header = (
            "import json\n"
            "from django.http import JsonResponse\n"
            "from django.views.decorators.csrf import csrf_exempt\n"
            "from django.shortcuts import get_object_or_404\n"
            "from django.template.loader import render_to_string\n"
            f"from .models import {model_names}\n\n"
        )

        blocks = [imports_header]
        for model in models:
            create_code = generate_create(model)
            delete_code = generate_delete(model)
            view_code = generate_views(model)
            put_code = generate_put(model)
            patch_code = generate_patch(model)

            block = (
                f"# ===== {model.__name__} =====\n"
                f"{create_code}\n"
                f"{delete_code}\n"
                f"{view_code}\n"
                f"{put_code}\n"
                f"{patch_code}\n"
            )
            blocks.append(block)

        final_code = "".join(blocks)

        views_file_path = os.path.join(app_config.path, 'views.py')

        try:
            with open(views_file_path, 'a', encoding='utf-8') as f:
                f.write(final_code)
            self.stdout.write(self.style.SUCCESS(f"Views geradas em {views_file_path}"))
        except IOError as erro:
            self.stderr.write(self.style.ERROR(f"Não foi possível escrever no arquivo: {erro}"))