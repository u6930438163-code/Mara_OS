# Live AI Desktop — integracja workerów

## Aktualny przepływ

1. Panel `Workery` tworzy sloty `chat` lub `diagnostics` w SQLite.
2. Osobna usługa `services.agent_workers` uruchamia pętle zarejestrowanych slotów.
3. `POST /api/worker-jobs` dodaje zadanie agenta do trwałej kolejki.
4. Po rozpoczęciu zadania worker publikuje `show` dla panelu `chat` lub `terminal` oraz `logs`.
5. `LiveDesktop.jsx` pobiera `GET /api/desktop/events?since=<id>` co około 2 sekundy.
6. `GET /api/worker-jobs` zwraca ostatnie zadania i statusy.

Wszystkie wymienione API poza `/api/health` wymagają nagłówka `Authorization: Bearer <MARA_SESSION_TOKEN>`.

Przykładowe żądanie:

```bash
curl -X POST http://127.0.0.1:8765/api/worker-jobs \
  -H "Authorization: Bearer $MARA_SESSION_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"agent":"Alex","kind":"diagnostics","payload":"system"}'
```

Do wykonania zadania potrzebny jest **aktywny slot** dla Alexa i rodzaju `diagnostics`, uruchomiony proces workerów oraz obsługiwany adapter diagnostyczny. W przeciwnym razie zadanie pozostanie w kolejce.

## Ważne ograniczenia

- Zdarzenia sterują wyłącznie panelami webowymi Mara_OS, nie natywnymi oknami KWin.
- Agenci nie planują jeszcze samodzielnie układu okien: zdarzenia są wywoływane przez cykl życia zadań.
- Zakończenie zadania nie zamyka panelu, aby zachować widoczność wyniku.
- Stan workerów w bazie jest stanem żądanym, a nie potwierdzeniem aktywnego procesu.
- Nie uruchomiono testów end-to-end na Debianie 13.
- Dalszy etap: odczyt rzeczywistych logów, podgląd jobów, synchronizacja okien wielu klientów, opcjonalny adapter KWin i bezpieczna polityka ukrywania paneli.
