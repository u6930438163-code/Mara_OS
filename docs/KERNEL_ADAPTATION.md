# Adaptacyjna warstwa Linux Kernel — Mara_OS

Mara_OS zachowuje **jedno jądro Linux** z Debiana 13. Polimorfizm istnieje już w interfejsach jądra (VFS, sterowniki, operacje sieciowe); nie oznacza automatycznego przełączania implementacji całego kernela.

## Zaimplementowane

- `services/kernel_adaptation.py`: wyłącznie odczyt z procfs, sysfs i cgroups v2; informacje o governorach CPU i dostępności eBPF.
- `services/resource_policy.py`: rekomendacje maksymalnej współbieżności workerów na podstawie pressure stall information, load average i liczby CPU.
- `GET /api/kernel/resources`: uwierzytelnione API, zwraca snapshot i rekomendację; nagłówek `Authorization: Bearer $MARA_SESSION_TOKEN`.

Przykład lokalny:

```bash
python3 -m services.kernel_adaptation
curl -H "Authorization: Bearer $MARA_SESSION_TOKEN" http://127.0.0.1:8765/api/kernel/resources
```

## Granice i następne etapy

- Brak automatycznego zapisu do `/proc/sys`, `/sys` lub cgroups. Rekomendacja ma `applied: false`.
- Brak loadera eBPF, modyfikacji schedulerów lub sterowników.
- Rejestr workerów i rekomendacje zasobów nie są jeszcze spięte automatycznym kontrolerem.
- Nie potwierdzono działania na docelowym Debianie 13 ani instalacji KDE.
- Zanim dodamy kontroler, należy sprawdzić limity kontenerów/cgroups, histerezę, bezpieczeństwo wyłączeń i testy integracyjne.

Wykorzystanie wspólnych interfejsów jądra pozostawia kompatybilność ze standardowym Linux Kernel i jego aktualizacjami.
