"""
Bot klikający w zadane miejsca na ekranie w określonych odstępach czasu.

Użycie:
    python klikacz.py --pozycja     # pokazuje na żywo współrzędne kursora
    python klikacz.py               # uruchamia klikanie wg konfiguracji poniżej

Zatrzymanie:
    - Ctrl+C w terminalu, albo
    - gwałtownie przesuń mysz do lewego górnego rogu ekranu (zabezpieczenie pyautogui).
"""

import sys
import time
import random

import pyautogui

# ----------------------------- KONFIGURACJA -----------------------------

# Każdy punkt: x, y – współrzędne na ekranie (użyj `--pozycja`, żeby je sprawdzić)
#              przerwa – ile sekund czekać PO tym kliknięciu
#              przycisk – "left", "right" lub "middle"
#              kliknięcia – 1 = pojedyncze, 2 = podwójne


POWTÓRZENIA = 0          # ile razy przejść całą listę; 0 = w nieskończoność
OPÓŹNIENIE_STARTU = 5    # sekundy na przełączenie się na właściwe okno
LOSOWY_JITTER = 0.5      # losowe +/- sekundy dodawane do przerwy (np. 0.3)
CZAS_RUCHU_MYSZY = 0.3   # jak długo mysz „jedzie" do punktu (sekundy)
PRZERWA_POMIEDZY_ABAWUWU_TAWERNA = 2.0  # sekundy na przełączenie się między Dr abawuwu a Tawerną
LEFT_CLICK = {"button": "left", "clicks": 1, "interval": 0.1}

ABAWUWU_TAWERNA_LOOP = [
    # Dr abawuwu
    {"x": 446, "y": 577, "przerwa": PRZERWA_POMIEDZY_ABAWUWU_TAWERNA},
    # Tawerna
    {"x": 200, "y": 325, "przerwa": PRZERWA_POMIEDZY_ABAWUWU_TAWERNA},
]

ABAWUWU_TAWERNA_LOOP_POWTÓRZENIA = 2  # ile razy powtarzać powyższy loop

PUNKTY = [
    # Telewizorek
    {"x": 665, "y": 215, "przerwa": 15.0},

    # Zamknięcie reklamy
    {"x": 1600, "y": 263, "przerwa": 2.0},

    # Loop Dr abawuwu - Tawerna
    *ABAWUWU_TAWERNA_LOOP * ABAWUWU_TAWERNA_LOOP_POWTÓRZENIA,
]
# ------------------------------------------------------------------------

pyautogui.FAILSAFE = True   # mysz w lewy górny róg = awaryjne zatrzymanie
pyautogui.PAUSE = 0.05


def pokaz_pozycje():
    print("Poruszaj myszą – widzisz bieżące współrzędne. Ctrl+C kończy.")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"\rX: {x:5d}  Y: {y:5d}", end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nKoniec.")


def uruchom():
    szer, wys = pyautogui.size()
    for p in PUNKTY:
        if not (0 <= p["x"] < szer and 0 <= p["y"] < wys):
            sys.exit(f"Punkt ({p['x']}, {p['y']}) jest poza ekranem {szer}x{wys}.")

    print(f"Start za {OPÓŹNIENIE_STARTU} s... (Ctrl+C lub mysz w lewy górny róg = stop)")
    time.sleep(OPÓŹNIENIE_STARTU)

    runda = 0
    try:
        while POWTÓRZENIA == 0 or runda < POWTÓRZENIA:
            runda += 1
            print(f"--- Runda {runda} ---")
            for p in PUNKTY:
                pyautogui.moveTo(p["x"], p["y"], duration=CZAS_RUCHU_MYSZY)
                pyautogui.click(
                    **LEFT_CLICK
                )
                print(f"Kliknięto ({p['x']}, {p['y']})")
                przerwa = p["przerwa"] + random.uniform(-LOSOWY_JITTER, LOSOWY_JITTER)
                time.sleep(max(0, przerwa))
    except KeyboardInterrupt:
        print("\nZatrzymano przez użytkownika.")
    except pyautogui.FailSafeException:
        print("\nZatrzymano (mysz w rogu ekranu).")


if __name__ == "__main__":
    if "--pozycja" in sys.argv:
        pokaz_pozycje()
    else:
        uruchom()