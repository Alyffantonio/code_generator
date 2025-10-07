from pathlib import Path
from django.apps import apps
from .build import build_urls
from .build_url_form import  build_urls_form

def create_urls(app_label: str, overwrite: bool = False, builder=None) -> Path:

    app_config = apps.get_app_config(app_label)

    urls_path = Path(app_config.path) / "urls.py"
    urls_path.parent.mkdir(parents=True, exist_ok=True)

    if urls_path.exists() and not overwrite:
        return urls_path

    if builder == "form":
        urls_code = build_urls_form(app_label)
    else :
        urls_code = build_urls(app_label)

    urls_path.write_text(urls_code, encoding="utf-8", newline="\n")

    return urls_path
