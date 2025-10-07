from django.apps import apps


def build_urls(app_label : str) -> str:
    app_config = apps.get_app_config(app_label)
    models = list(app_config.get_models())

    header = (
        "from django.urls import path\n"
        "from . import views \n\n"
        "urlpatterns = [\n"
    )
    lines = []
    for model in models:
        ml = model.__name__.lower()
        lines.append(f"    path('{ml}/', views.{ml}_view_api, name='{ml}_list'),")
        lines.append(f"    path('{ml}/post/', views.{ml}_create_api, name='{ml}_post'),")
        lines.append(f"    path('{ml}/delete/<int:id_object>/', views.{ml}_delete_api, name='{ml}_delete'),")
        lines.append(f"    path('{ml}/put/<int:id_object>/', views.{ml}_put_api, name='{ml}_put'),")
        lines.append(f"    path('{ml}/patch/<int:id_object>/', views.{ml}_patch_api, name='{ml}_patch'),")

    footer = "\n]\n"
    return header + "\n".join(lines) + footer
