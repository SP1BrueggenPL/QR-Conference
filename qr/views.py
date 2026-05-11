# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _, activate
from django.templatetags.static import static
from django.contrib.staticfiles import finders

# ------ zasoby/utility ------

def find_step_image(room_slug: str, step_number: int, role: str | None = None):
    """
    Szuka obrazka w kolejności:
    steps/<room>/<role>/<n>.png|jpg  -> steps/<room>/<n>.png|jpg  -> images/<room>/<n>.png|jpg
    """
    room = (room_slug or "").lower().strip()
    role = (role or "").lower().strip()

    candidates = []
    if role in ("employee", "external"):
        candidates += [
            f"steps/{room}/{role}/{step_number}.png",
            f"steps/{room}/{role}/{step_number}.jpg",
        ]

    candidates += [
        f"steps/{room}/{step_number}.png",
        f"steps/{room}/{step_number}.jpg",
        f"images/{room}/{step_number}.png",   # stary fallback, opcjonalny
        f"images/{room}/{step_number}.jpg",
    ]

    for relpath in candidates:
        if finders.find(relpath):
            return static(relpath)
    return None



def get_steps(lang: str, room_slug: str, role: str):
    """
    Zwraca listę kroków dla (sala, rola, język).
    role: 'employee' | 'external'
    """
    # Możesz rozbić treści per rola — poniżej przykład z Twoich tekstów:
    employee_creative = [
        _("<strong>Creative Room - Preparation</strong>"),
        _("Check room availability on the screen before entering – it shows the current reservation status. You can reserve the room using this device."),
        _("After entering the room, it may be necessary to turn on the screen power – you can do this with the buttons on the wall between the screens."),
        _("<strong>Creative Room - Start a Conference</strong>"),
        _("We can start the meeting using the Panel on the table – just press the join button. <strong>*A meeting must be created on Teams.</strong> Image and sound are transmitted via conference equipment installed in the room."),
        _("If you want to share your screen, use the device below."),
        _("After connecting the device, it will appear like a USB drive in File Explorer."),
        _("After starting the application on the USB adapter, a window will appear showing the system is ready for screen sharing. Then press the button on the adapter – it will light up green. Sound should also be transmitted through the conference system."),
        _("You can also use the HDMI cables present in the room (labeled). <strong>Please do not switch them.</strong>"),
        _("<strong>HDMI PROJECTOR</strong> -> turn on the projector with the remote and make sure HDMI2 is selected as the source."),
        _("<strong>HDMI TV</strong> -> This cable is for the right-side screen, ensure the TV source is set to PC (DVI)."),
        _("You can also use the computer in the room. Ensure the right screen has the Videoconference source selected. Use the keyboard and mouse in the room to log into Windows and then BWP. <strong>When using a computer, remember to log out at the end of the meeting.</strong>"),
        _("<strong>Scan the QR code for IT Support if you need help.</strong>"),
    ]

    external_creative = [
        _("<strong>Creative Room - Preparation</strong>"),
        _("After entering the room, it may be necessary to turn on the screen power – you can do this with the buttons on the wall between the screens."),
        _("<strong>Creative Room - Start a Conference</strong>"),
        _("If you want to share your screen, use the device below."),
        _("After connecting the device, it will appear like a USB drive in File Explorer."),
        _("After starting the application on the USB adapter, a window will appear showing the system is ready for screen sharing. Then press the button on the adapter – it will light up green. Sound should also be transmitted through the conference system."),
        _("You can also use the HDMI cables present in the room (labeled). <strong>Please do not switch them.</strong>"),
        _("<strong>HDMI PROJECTOR</strong> -> turn on the projector with the remote and make sure HDMI2 is selected as the source."),
        _("<strong>HDMI TV</strong> -> This cable is for the right-side screen, ensure the TV source is set to PC (DVI)."),
        _("<strong>Scan the QR code for IT Support if you need help.</strong>"),
    ]

    employee_vip = [
        _("<strong>VIP Room - Preparation</strong>"),
        _("Check room availability on the screen before entering – it shows the current reservation status. You can reserve the room using this device."),
        _("After entering the room, it may be necessary to turn on the projector power – you can do this with the wall buttons."),
        _("<strong>VIP Room - Start a Conference</strong>"),
        _("We can start the meeting using the Panel on the table – just press the join button. <strong>*A meeting must be created on Teams.</strong> Image and sound are transmitted via conference equipment installed in the room."),
        _("If you want to share your screen, use the device below."),
        _("After connecting the device, it will appear like a USB drive in File Explorer."),
        _("After starting the application on the USB adapter, a window will appear showing the system is ready for screen sharing. Then press the button on the adapter – it will light up green. Sound should also be transmitted through the conference system."),
        _("Use the computer located under the table near the screen. Ensure the right screen has HDMI2 selected as the source. Operate the computer using the keyboard and mouse available in the room. Log into Windows and then BWP. <strong>When using a computer, remember to log out at the end of the meeting.</strong>"),
        _("<strong>Scan the QR code for IT Support if you need help.</strong>"),
    ]

    external_vip = [
        _("<strong>VIP Room - Preparation</strong>"),
        _("After entering the room, it may be necessary to turn on the projector power – you can do this with the wall buttons."),
        _("<strong>VIP Room - Start a Conference</strong>"),
        _("If you want to share your screen, use the device below."),
        _("After connecting the device, it will appear like a USB drive in File Explorer."),
        _("After starting the application on the USB adapter, a window will appear showing the system is ready for screen sharing. Then press the button on the adapter – it will light up green. Sound should also be transmitted through the conference system."),
        _("<strong>Scan the QR code for IT Support if you need help.</strong>"),
    ]

    # różnicowanie po roli – przykładowo: dla pracownika dorzuć 1-2 kroki BHP/korpo,
    # dla zewnętrznego gościa dorzuć skrócone wskazówki
    if room_slug == "kreatywna":
        if role == "employee":
            return employee_creative
        else:  # external
            return external_creative
    elif room_slug == "vip":
        if role == "employee":
            return employee_vip
        else:
            return external_vip
    return []

# ------ FLOW widoki ------

def start(request):
    # Ekran startowy
    return render(request, "start.html")

def choose_room(request):
    # Strona do ręcznego wyboru sali (także jako źródło do generowania QR)
    return render(request, "choose_room.html")

def choose_language(request, room_slug):
    # Wejście zwykle z QR: /kiosk/room/<sala>/language/
    if request.method == "POST":
        lang = request.POST.get("language", "pl").lower()
        # Wymuś aktywację i zapisz w sesji (opcjonalnie)
        activate(lang)
        request.session["django_language"] = lang
        return redirect("kiosk:choose_role", room_slug=room_slug, lang=lang)

    # GET – pokaż wybór języka
    current = request.session.get("django_language", "pl")
    activate(current)
    return render(request, "choose_language.html", {"room_slug": room_slug})

def choose_role(request, room_slug, lang):
    activate(lang)
    if request.method == "POST":
        role = request.POST.get("role")  # 'employee' | 'external'
        if role in ("employee", "external"):
            return redirect("kiosk:step", room_slug=room_slug, lang=lang, role=role, step=1)
    return render(request, "choose_role.html", {"room_slug": room_slug, "lang": lang})

def show_step(request, room_slug, lang, role, step: int):
    activate(lang)

    steps = get_steps(lang, room_slug.lower(), role.lower())
    total = len(steps)
    if total == 0:
        return redirect("kiosk:choose_language", room_slug=room_slug)

    # out of range → do finish
    if step < 1:
        return redirect("kiosk:step", room_slug=room_slug, lang=lang, role=role, step=1)
    if step > total:
        return redirect("kiosk:finish")

    text = steps[step - 1]
    image_url = find_step_image(room_slug.lower(), step, role=role)

    # Linki wprzód/wstecz
    prev_url = (
        reverse("kiosk:step", kwargs=dict(room_slug=room_slug, lang=lang, role=role, step=step - 1))
        if step > 1 else None
    )
    next_url = (
        reverse("kiosk:step", kwargs=dict(room_slug=room_slug, lang=lang, role=role, step=step + 1))
        if step < total else reverse("kiosk:finish")
    )

    ctx = {
        "room": room_slug.title(),
        "lang": lang,
        "role": role,
        "step": step,
        "total_steps": total,
        "step_text": text,
        "step_image": image_url,
        "prev_url": prev_url,
        "next_url": next_url,
        "is_last": step == total,
    }
    return render(request, "step.html", ctx)

def finish(request):
    # Próba zamknięcia przeglądarki (działa w trybie kiosk/okno otwarte przez skrypt)
    return render(request, "finish.html")
