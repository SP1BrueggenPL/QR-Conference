# urls.py
from django.urls import path
from . import views

app_name = "kiosk"

urlpatterns = [
    path("", views.start, name="start"),
    # Ekran wyboru sali (opcjonalny – do generowania QR)
    path("room/", views.choose_room, name="choose_room"),

    # Punkt wejścia z QR: /kiosk/room/<sala>/language/
    path("room/<slug:room_slug>/language/", views.choose_language, name="choose_language"),

    # Wybór roli po języku
    path("room/<slug:room_slug>/lang/<slug:lang>/role/", views.choose_role, name="choose_role"),

    # Kroki instrukcji jako osobne widoki:
    path(
        "room/<slug:room_slug>/lang/<slug:lang>/role/<slug:role>/step/<int:step>/",
        views.show_step,
        name="step",
    ),

    # Zakończenie – zamknięcie przeglądarki
    path("finish/", views.finish, name="finish"),
]
