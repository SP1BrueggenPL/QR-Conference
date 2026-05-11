# qr/po_i18n.py
import os
from functools import lru_cache
from django.conf import settings

PO_PATH = os.path.join(settings.BASE_DIR, "i18n", "messages.po")

def _unquote(s: str) -> str:
    # usuwa cudzysłowy i interpretuje \" \n etc.
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s.encode('utf-8').decode('unicode_escape')

@lru_cache(maxsize=1)
def _load_po_map():
    """
    Bardzo prosty parser pliku .po: obsługuje bloki msgid/msgstr + wielolinijkowe wartości.
    Zwraca dict {msgid: msgstr}.
    """
    if not os.path.exists(PO_PATH):
        return {}

    mapping = {}
    current_id = []
    current_str = []
    mode = None  # 'id' lub 'str'

    with open(PO_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            if line.startswith('msgid '):
                # zapis poprzedniego bloku, jeśli był
                if current_id or current_str:
                    msgid = "".join(current_id).strip()
                    msgstr = "".join(current_str).strip()
                    if msgid:
                        mapping[msgid] = msgstr
                # nowy blok
                current_id, current_str = [], []
                mode = 'id'
                current_id.append(_unquote(line[len('msgid '):]))
                continue

            if line.startswith('msgstr '):
                mode = 'str'
                current_str.append(_unquote(line[len('msgstr '):]))
                continue

            # kontynuacje wielolinijkowe
            if line.startswith('"') and line.endswith('"'):
                if mode == 'id':
                    current_id.append(_unquote(line))
                elif mode == 'str':
                    current_str.append(_unquote(line))
                continue

            # pusta linia = koniec bloku
            if line == "":
                if current_id or current_str:
                    msgid = "".join(current_id).strip()
                    msgstr = "".join(current_str).strip()
                    if msgid:
                        mapping[msgid] = msgstr
                current_id, current_str, mode = [], [], None

        # flush ostatniego bloku
        if current_id or current_str:
            msgid = "".join(current_id).strip()
            msgstr = "".join(current_str).strip()
            if msgid:
                mapping[msgid] = msgstr

    return mapping

def get_translator(lang: str):
    """
    Zwraca funkcję tr(msgid) -> tekst.
    - Jeśli lang == 'pl' i jest tłumaczenie w .po → zwrot msgstr
    - W innym przypadku → zwrot msgid (angielski)
    """
    po_map = _load_po_map()

    def tr(msgid: str) -> str:
        if lang == 'pl':
            return po_map.get(msgid, msgid)  # fallback do msgid, jeśli brak
        return msgid  # EN (msgid) albo dowolny inny język
    return tr
