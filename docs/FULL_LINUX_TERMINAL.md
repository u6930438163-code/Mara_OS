# Mara_OS — pełny terminal Linux

W Mara_OS istnieją dwa różne interfejsy terminalowe:

1. **KDE Konsole** — prawdziwy terminal interaktywny, uruchamia powłokę użytkownika i wszystkie zainstalowane narzędzia Linux, bez sztucznej listy dozwolonych poleceń. Standardowe uprawnienia użytkownika, `sudo` po uwierzytelnieniu.
2. **Mara Shell** (`shell/mara_shell.py`) — osobny, ograniczony interfejs diagnostyczny dla AI. Nie zastępuje powłoki systemowej.

## Instalacja na Debianie 13

```bash
sudo bash scripts/install-linux-terminal.sh
bash scripts/open-linux-terminal.sh
```

Instalator dodaje Konsole, Bash, bash-completion, standardowe narzędzia Linux, SSH, Git, Python 3 i `parted`.

Przykładowe polecenia w prawdziwej konsoli:

```bash
uname -a
lsblk -f
sudo parted -l
sudo apt update
systemctl --failed
journalctl -b --no-pager
git status
python3 --version
```

GParted to graficzny program; można go uruchomić z terminala komendą `gparted`, jeśli jest zainstalowany i działa sesja graficzna.

**Uwaga:** modyfikowanie partycji, formatowanie, `rm` i zmiany usług systemowych mogą zniszczyć dane lub przerwać działanie systemu. Agenci AI nie otrzymują automatycznie `sudo` ani możliwości wykonywania dowolnych komend w powłoce użytkownika.

## Ograniczenie obecnego web GUI

Zakładka Terminal w `src/main.jsx` jest nadal demonstracją. Zwykła strona WWW nie może bezpiecznie uruchamiać natywnej powłoki w sesji użytkownika. Integracja terminala w przeglądarce wymaga osobnego serwera PTY, uwierzytelniania, obsługi sesji i audytu. Skrypty powyżej uruchamiają prawdziwy terminal **lokalnie na Debianie 13**, a nie w podglądzie webowym.
