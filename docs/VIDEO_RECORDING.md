# Mara_OS — nagrywanie wideo i Real Vision

## Dostępne funkcje

Panel **Real Vision** zawiera nagrywarkę ekranu i kamery. Nagrywanie jest uruchamiane ręcznie po wyrażeniu zgody w przeglądarce. Maksymalny czas pojedynczego nagrania wynosi 60 sekund. Dźwięk nie jest przechwytywany. Plik pozostaje lokalnie w przeglądarce, dopóki użytkownik go nie pobierze.

Przycisk **Przekaż nagranie do analizy Vision** przekazuje lokalny plik do ekstrakcji trzech klatek (10%, 50%, 90% długości filmu). Sam plik wideo nie jest wysyłany do backendu. Kliknięcie **Analizuj obraz** przesyła klatki osobno do `/api/ai/vision`.

Można opcjonalnie zapisać tekstowe wyniki analiz w SQLite oraz przekazać je jako `vision_report` do kolejki workera wybranego agenta. Do wykonania zadań trzeba uruchomić osobny proces `python3 -m services.agent_workers` i utworzyć slot `vision_report` dla wybranego agenta.

## Konfiguracja

- Wymagany HTTPS lub localhost, przeglądarka obsługująca MediaRecorder i getUserMedia/getDisplayMedia.
- `MARA_SESSION_TOKEN` jest wymagany do autoryzacji API.
- Dla lokalnej Ollamy ustaw `MARA_VISION_PROVIDER=ollama` i uruchom model zgodny z `MARA_OLLAMA_VISION_MODEL` (domyślnie `llama3.2-vision:11b`).
- Przeglądarka może nie obsługiwać nagrywania ekranu na niektórych urządzeniach mobilnych.
- Wybór agenta nie oznacza automatycznego wykonania zadania. Worker wymaga działającego procesu i konfiguracji dostawcy tekstowego AI.

## Testy

```bash
python3 -m unittest discover -s tests -p 'test_vision*.py'
python3 -m unittest discover -s tests -p 'test_ollama_vision.py'
npm install
npm run build
```

Te polecenia są instrukcją weryfikacji, nie potwierdzeniem ich wykonania.

## Ograniczenia

To nie jest generowanie filmów z promptu, ani automatyczne nagrywanie pulpitu przez agenta bez udziału użytkownika. Nie ma ciągłej analizy obrazu na żywo. Historia SQLite zawiera tekst analiz, nie klatki ani wideo. Nie przechowuj sekretów w repozytorium.
