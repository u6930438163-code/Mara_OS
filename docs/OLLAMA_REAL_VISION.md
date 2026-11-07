# Mara_OS — Ollama Real Vision

Backend: `services/ai.py`, endpoint `POST /api/ai/vision` (Bearer `MARA_SESSION_TOKEN`).

## Debian 13 — instalacja

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
ollama pull llama3.2-vision:11b
ollama pull hf.co/mradermacher/Floppa-12B-Gemma3-Uncensored-GGUF:Q8_0
ollama list
```

Ollama musi działać lokalnie na `127.0.0.1:11434`. Nie wystawiaj portu 11434 publicznie.

## Konfiguracja serwera

```bash
export MARA_SESSION_TOKEN='ustaw-wlasny-losowy-token'
export MARA_VISION_PROVIDER=ollama
export MARA_OLLAMA_VISION_MODEL=llama3.2-vision:11b
export MARA_TEXT_PROVIDER=ollama
export MARA_OLLAMA_TEXT_MODEL='hf.co/mradermacher/Floppa-12B-Gemma3-Uncensored-GGUF:Q8_0'
python3 server.py
```

Domyślnie tekst nadal korzysta z OpenAI, dopóki nie ustawisz `MARA_TEXT_PROVIDER=ollama`; Vision domyślnie korzysta z Ollamy. `MARA_VISION_PROVIDER=openai` przywraca wcześniejszy adapter OpenAI.

## Test

```bash
curl -fsS http://127.0.0.1:11434/api/tags
```

Dla Vision wyślij `POST /api/ai/vision` z JSON `{"question":"Co jest na obrazie?","image":"data:image/png;base64,..."}` oraz nagłówkiem `Authorization: Bearer <MARA_SESSION_TOKEN>`. API przyjmuje obrazy PNG/JPEG/WEBP w postaci data URL. Przechwytywanie kamery, ekranu i klatek wideo wymaga osobnego modułu.

## Status

Integracja backendowa jest zapisana w repozytorium. Pobranie modeli, testy sprzętowe i uruchomienie na docelowej maszynie pozostają do wykonania.
