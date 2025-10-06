from django.apps import apps


def generate_imports(app_label: str) -> str:

    try:
        app_config = apps.get_app_config(app_label)
        models = list(app_config.get_models())
    except LookupError:
        return f"# ERRO: App '{app_label}' não encontrada."

    if not models:
        return f"# AVISO: Nenhum modelo encontrado na app '{app_label}'."

    form_names = [f"{model.__name__}Form" for model in models]
    import_lines = [
        "from django.shortcuts import render, redirect",
        "from django.views.decorators.csrf import csrf_exempt",  # Se estiver usando
        f"from .forms import {', '.join(form_names)}"
    ]
    return "\n".join(import_lines)


def generate_form_imports(app_label: str) -> str:

    try:
        app_config = apps.get_app_config(app_label)
        models = list(app_config.get_models())
    except LookupError:
        return f"# ERRO: App '{app_label}' não encontrada."

    if not models:
        return f"# AVISO: Nenhum modelo encontrado na app '{app_label}'."

    model_names = [model.__name__ for model in models]

    import_lines = [
        "from django import forms",
        f"from {app_label}.models import {', '.join(model_names)}"
    ]

    return "\n".join(import_lines)