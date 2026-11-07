# Mara_OS

Mara_OS — projekt środowiska Debian 13 z KDE Plasma, agentami AI i Live AI Desktop.

## Domyślne narzędzia systemowe

- **OpenSSH Server** — instalacja i automatyczny start z Debianem 13: `sudo bash scripts/install-ssh-server.sh`. [Instrukcja](docs/SSH_SERVER.md).

- **GParted** — domyślny graficzny edytor partycji. Instalacja na Debianie 13: `sudo bash scripts/install-gparted.sh`. Wersja pochodzi z oficjalnego APT, bez sztywnego przypinania. [Instrukcja](docs/GPARTED.md).

> Samo zapisanie instalatora w repozytorium nie oznacza, że GParted jest już zainstalowany na docelowym systemie.
