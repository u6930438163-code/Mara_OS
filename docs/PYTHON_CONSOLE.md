# Mara_OS — Python Console

Lokalny kompilator i wykonawca programów Python: `shell/python_console.py`.

## Przykłady

```bash
# Weryfikacja składni bez wykonywania
python3 -m shell.python_console ./examples/demo.py --compile-only

# Uruchomienie z uprawnieniami zwykłego użytkownika
python3 -m shell.python_console ./examples/demo.py --timeout 30

# Świadome uruchomienie przez operatora z prawami root
sudo python3 -m shell.python_console ./examples/demo.py --timeout 30
```

Wymagane jest istniejące źródło `.py`. Moduł kompiluje je przez `py_compile`, po czym uruchamia osobny proces Python. Program może używać `subprocess.run([...])` do uruchamiania poleceń systemowych. Nie jest to piaskownica: programy uruchomione jako root mają pełne uprawnienia konta root.

Konsola jest narzędziem **lokalnego terminala**. Celowo nie udostępnia zdalnego API wykonującego dowolny kod, nie eskaluje uprawnień samodzielnie i nie przechowuje hasła administratora. Kontroluj, jakie pliki uruchamiasz jako root.

Limit rozmiaru źródła: 256 kB. Limit czasu wykonania: 1–120 s. Wyniki stdout i stderr są obcinane do 64 kB na strumień. Limit czasu nie jest granicą bezpieczeństwa dla procesów potomnych uruchamianych przez skrypt.

Testy:

```bash
python3 -m unittest tests.test_python_console
```
