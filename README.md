# Mara_OS

Mara_OS — projekt środowiska Debian 13 z KDE Plasma, agentami AI i Live AI Desktop.

## Domyślne narzędzia systemowe

- **OpenSSH Server** — instalacja i automatyczny start z Debianem 13: `sudo bash scripts/install-ssh-server.sh`. [Instrukcja](docs/SSH_SERVER.md).

- **GParted** — domyślny graficzny edytor partycji. Instalacja na Debianie 13: `sudo bash scripts/install-gparted.sh`. Wersja pochodzi z oficjalnego APT, bez sztywnego przypinania. [Instrukcja](docs/GPARTED.md).

> Samo zapisanie instalatora w repozytorium nie oznacza, że GParted jest już zainstalowany na docelowym systemie.

## Uruchomienie podglądu deweloperskiego (Codespaces / Debian)

Wymagane: Python 3.11+, Node.js 20+ i npm. W dwóch terminalach w katalogu repozytorium:

**Terminal 1 — API:**

```bash
export MARA_SESSION_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "Zapisz token sesji z tej powłoki w bezpiecznym miejscu; nie publikuj go."
python3 server.py
```

**Terminal 2 — interfejs:**

```bash
npm install
npm run dev -- --host 0.0.0.0
```

Otwórz przekierowany port Vite (zwykle 5173) w Codespaces. Port API 8765 pozostaw prywatny; Vite przekazuje żądania `/api` na `127.0.0.1:8765`. W polu tokenu w zakładce Czat wprowadź dokładną wartość `MARA_SESSION_TOKEN` z pierwszego terminala (możesz ją wcześniej wygenerować i zapisać prywatnie).

Ollama jest opcjonalna dla samego podglądu GUI. Aby uzyskać odpowiedzi AI, uruchom Ollamę na tej samej maszynie i zainstaluj model wskazany przez `MARA_OLLAMA_TEXT_MODEL`, albo ustaw `GEMINI_API_KEY` jako sekret środowiska. Nie zapisuj kluczy w repozytorium.

**Ograniczenia:** to aplikacja deweloperska, nie obraz instalacyjny Debian/ISO. Czat i menedżer modeli wymagają działającego API, tokenu i odpowiedniego dostawcy AI. Terminal GUI jest nadal demonstracyjny. Nie potwierdzono jeszcze pełnego testu startowego w Codespaces.
