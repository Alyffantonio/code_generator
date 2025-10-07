from django.apps import apps


def build_urls_form(app_label : str) -> str:
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
        lines.append(f"    path('{ml}/', views.{ml}_read, name='{ml}_list'),")
        lines.append(f"    path('{ml}/<int:id_object>/', views.{ml}_details, name='{ml}_details'),")
        lines.append(f"    path('{ml}/create/', views.{ml}_create, name='{ml}_create'),")
        lines.append(f"    path('{ml}/update/', views.{ml}_update, name='{ml}_update'),")
        lines.append(f"    path('{ml}/delete/<int:id_object>/', views.{ml}_delete, name='{ml}_delete'),")


    footer = "\n]\n"
    return header + "\n".join(lines) + footer
