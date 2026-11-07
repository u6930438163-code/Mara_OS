# Mara_OS — architektura i zasady implementacji

Mara_OS jest niezależnym projektem opartym o Debian 13 Trixie. Kod warstwy Mara_OS powstaje od podstaw; inne repozytoria użytkownika służą wyłącznie jako źródła wymagań i inspiracji architektonicznych.

## Zasady

- Nie modyfikować Bastilla_1_2, Debian_13_Trixie ani Debian_13_orginal.
- Brak Gemini i silnika deterministycznego; dostawcy AI: OpenAI API oraz opcjonalna Ollama.
- Aria, Alex, Astyria i Aurelius: równorzędni uczestnicy jednej kolejki zadań; atomowy przydział jednego zadania jednemu workerowi, możliwość recenzji przez pozostałych.
- API i sekrety po stronie serwera, autoryzacja i ograniczenie uprawnień.
- Żadnego wykonywania poleceń administratora bez jawnej akceptacji operatora.
- GUI: Violet Blade, fioletowo-różowa paleta, interaktywne logo M bez miecza.
- Tapeta dostarczona przez użytkownika wymaga sprawdzenia praw przed publiczną dystrybucją.
- Gotowość ISO potwierdzamy dopiero po budowie i testach rozruchu.

## Plan integracji

1. Podstawowa aplikacja React + Node API i testy.
2. Trwała kolejka zadań, kontrola współbieżności i integracja oryginalnych workerów.
3. OpenAI/Ollama, diagnostyka, terminal i menedżer pakietów.
4. Debian live-build, XFCE, pakiety DEB i testy ISO w QEMU.

Prototyp v0.4 jest przygotowany lokalnie; ten dokument nie potwierdza publikacji całego kodu ani uruchomienia workerów.
