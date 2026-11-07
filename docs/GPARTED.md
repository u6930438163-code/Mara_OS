# GParted — domyślny edytor partycji Mara_OS

Mara_OS opiera się na Debianie 13. Domyślnym graficznym edytorem partycji jest **GParted** z oficjalnego repozytorium APT. Nie przypinamy sztywnej wersji: `apt` wybiera najlepszą wersję zgodną z repozytoriami i aktualizacjami Debiana 13.

## Instalacja na docelowym systemie

```bash
sudo bash scripts/install-gparted.sh
```

Skrypt sprawdza Debian 13, aktualizuje indeks pakietów, sprawdza wersję kandydującą i instaluje pakiet `gparted`. Nie wykonuje żadnych operacji na partycjach.

Uruchamianie z KDE Plasma: menu aplikacji → GParted, albo `gparted` z odpowiednim uwierzytelnieniem administratora.

## Integracja z AI

- Agenci mogą odczytywać diagnostykę dysków poprzez osobne adaptery tylko do odczytu.
- Uruchomienie graficznego edytora nie oznacza zgody na formatowanie, kasowanie lub zmianę rozmiaru partycji.
- Przed zmianą tablicy partycji należy zapewnić kopię danych i sprawdzić poprawny dysk.
- Zmiana partycji systemowej w użyciu może wymagać środowiska live USB.

Stan: instalator i dokumentacja zapisane w repozytorium. Nie potwierdzono instalacji GParted na rzeczywistym komputerze ani uruchomienia sesji KDE.
