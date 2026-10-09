"""
KLIKACZ – bot klikający w wybrane miejsca na ekranie.

Sekwencja jednej rundy:
    1. Telewizorek
    2. Zamknięcie reklamy
    3. Pętla: Dr abawuwu -> Tawerna (powtarzana kilka razy)

Pozycje i przerwy zapisują się w pliku klikacz_ustawienia.json obok programu.
"""

import json
import os
import random
import sys
import time

import pyautogui

# ----------------------------- USTAWIENIA PROGRAMISTY -----------------------------

POWTÓRZENIA = 0            # ile razy przejść całą sekwencję; 0 = w nieskończoność
OPÓŹNIENIE_STARTU = 5      # sekundy na przełączenie się na właściwe okno
LOSOWY_JITTER = 0.5        # losowe +/- sekundy dodawane do każdej przerwy
CZAS_RUCHU_MYSZY = 0.3     # jak długo mysz „jedzie" do punktu (sekundy)
LEFT_CLICK = {"button": "left", "clicks": 1, "interval": 0.1}

PĘTLA_POWTÓRZENIA = 2      # domyślnie: ile razy powtarzać pętlę Dr abawuwu - Tawerna

# Punkty, których pozycję ustawia użytkownik: (klucz, nazwa, domyślna przerwa po kliknięciu)
PUNKTY_POCZĄTEK = [
    ("telewizorek", "Telewizorek", 15.0),
    ("reklama", "Zamknięcie reklamy", 2.0),
]
PUNKTY_PĘTLA = [
    ("abawuwu", "Dr abawuwu", 2.0),
    ("tawerna", "Tawerna", 2.0),
]

# ----------------------------------------------------------------------------------

pyautogui.FAILSAFE = True   # mysz w lewy górny róg = awaryjne zatrzymanie
pyautogui.PAUSE = 0.05


def folder_programu():
    # Działa zarówno jako zwykły skrypt, jak i jako spakowany .exe
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


PLIK = os.path.join(folder_programu(), "klikacz_ustawienia.json")


def zapytaj_liczbe(pytanie, domyslna, minimum=0.0, calkowita=False):
    while True:
        tekst = input(f"{pytanie} [Enter = {domyslna}]: ").strip().replace(",", ".")
        if tekst == "":
            return domyslna
        try:
            wartosc = float(tekst)
            if wartosc < minimum:
                print(f"  Podaj liczbę nie mniejszą niż {minimum}.")
                continue
            return int(wartosc) if calkowita else wartosc
        except ValueError:
            print("  To nie jest liczba, spróbuj jeszcze raz.")


def konfiguracja():
    print("\n=== KONFIGURACJA ===")
    print("Dla każdego miejsca najedź myszką na właściwy punkt na ekranie")
    print("i naciśnij Enter w tym oknie.\n")

    wszystkie = PUNKTY_POCZĄTEK + PUNKTY_PĘTLA
    punkty = {}
    for i, (klucz, nazwa, domyslna_przerwa) in enumerate(wszystkie, 1):
        print(f"--- {i}/{len(wszystkie)}: {nazwa} ---")
        input(f"Najedź myszką na „{nazwa}” i naciśnij Enter...")
        x, y = pyautogui.position()
        print(f"  Zapisano pozycję: X={x}, Y={y}")
        przerwa = zapytaj_liczbe(f"  Ile sekund czekać po kliknięciu „{nazwa}”?",
                                 domyslna_przerwa, minimum=0.1)
        punkty[klucz] = {"x": x, "y": y, "przerwa": przerwa}
        print()

    petla = zapytaj_liczbe("Ile razy powtórzyć pętlę Dr abawuwu - Tawerna w każdej rundzie?",
                           PĘTLA_POWTÓRZENIA, minimum=1, calkowita=True)

    ustawienia = {"punkty": punkty, "petla_powtorzenia": petla}
    try:
        with open(PLIK, "w", encoding="utf-8") as f:
            json.dump(ustawienia, f, indent=2, ensure_ascii=False)
        print("\nUstawienia zapisane – następnym razem nie trzeba ich wpisywać od nowa.")
    except OSError:
        print("\nNie udało się zapisać ustawień (program będzie działał, ale ich nie zapamięta).")
    return ustawienia


def wczytaj():
    try:
        with open(PLIK, encoding="utf-8") as f:
            dane = json.load(f)
        wymagane = [k for k, _, _ in PUNKTY_POCZĄTEK + PUNKTY_PĘTLA]
        if all(k in dane["punkty"] for k in wymagane) and dane["petla_powtorzenia"] >= 1:
            return dane
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def pokaz(ustawienia):
    print("\nZapisane ustawienia:")
    for klucz, nazwa, _ in PUNKTY_POCZĄTEK + PUNKTY_PĘTLA:
        p = ustawienia["punkty"][klucz]
        print(f"  {nazwa}: pozycja ({p['x']}, {p['y']}), przerwa {p['przerwa']} s")
    print(f"  Pętla Dr abawuwu - Tawerna: {ustawienia['petla_powtorzenia']}x na rundę")


def zbuduj_sekwencje(ustawienia):
    """Składa listę kliknięć jednej rundy: początek + pętla powtórzona N razy."""
    p = ustawienia["punkty"]
    poczatek = [{"nazwa": n, **p[k]} for k, n, _ in PUNKTY_POCZĄTEK]
    petla = [{"nazwa": n, **p[k]} for k, n, _ in PUNKTY_PĘTLA]
    return poczatek + petla * ustawienia["petla_powtorzenia"]


def klikaj(ustawienia):
    sekwencja = zbuduj_sekwencje(ustawienia)

    szer, wys = pyautogui.size()
    for p in sekwencja:
        if not (0 <= p["x"] < szer and 0 <= p["y"] < wys):
            print(f"\nPunkt „{p['nazwa']}” ({p['x']}, {p['y']}) jest poza ekranem "
                  f"{szer}x{wys}. Ustaw miejsca od nowa (opcja n).")
            return

    print(f"\nSTART za {OPÓŹNIENIE_STARTU} sekund. Przełącz się na właściwe okno!")
    print("ABY ZATRZYMAĆ: gwałtownie przesuń mysz do LEWEGO GÓRNEGO ROGU ekranu")
    print("               albo naciśnij Ctrl+C w tym oknie.")
    for s in range(OPÓŹNIENIE_STARTU, 0, -1):
        print(f"  {s}...")
        time.sleep(1)

    runda = 0
    try:
        while POWTÓRZENIA == 0 or runda < POWTÓRZENIA:
            runda += 1
            print(f"--- Runda {runda} ---")
            for p in sekwencja:
                pyautogui.moveTo(p["x"], p["y"], duration=CZAS_RUCHU_MYSZY)
                pyautogui.click(**LEFT_CLICK)
                print(f"Kliknięto: {p['nazwa']} ({p['x']}, {p['y']})")
                przerwa = p["przerwa"] + random.uniform(-LOSOWY_JITTER, LOSOWY_JITTER)
                time.sleep(max(0, przerwa))
        print("\nGotowe – wszystkie powtórzenia wykonane.")
    except KeyboardInterrupt:
        print("\nZatrzymano (Ctrl+C).")
    except pyautogui.FailSafeException:
        print("\nZatrzymano (mysz w rogu ekranu).")


def main():
    print("=" * 40)
    print("   KLIKACZ – automatyczne klikanie")
    print("=" * 40)

    ustawienia = wczytaj()
    if ustawienia:
        pokaz(ustawienia)
        wybor = input("\nUruchomić z tymi ustawieniami? (Enter = tak, n = ustaw od nowa): ")
        if wybor.strip().lower() == "n":
            ustawienia = konfiguracja()
    else:
        print("\nPierwsze uruchomienie – najpierw ustawimy, gdzie klikać.")
        ustawienia = konfiguracja()

    klikaj(ustawienia)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # żeby okno nie zniknęło przy błędzie
        print(f"\nWystąpił błąd: {e}")
    input("\nNaciśnij Enter, aby zamknąć...")