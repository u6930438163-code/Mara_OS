# Mara_OS — autonomia właściciela i polityka działania AI

Mara_OS nie dodaje własnej warstwy arbitralnego filtrowania tematów rozmów ani klasyfikatora moralnego. Rozmowy nie są blokowane przez lokalną listę tematów zabronionych. Właściciel wybiera dostawcę modelu, o ile jest dostępny i poprawnie skonfigurowany.

## Rozdzielenie warstw

- **Rozmowa**: swoboda dyskusji; Mara_OS nie implementuje dodatkowego filtra treści.
- **Dostawca modelu**: zewnętrzne API może stosować własne reguły, których Mara_OS nie kontroluje ani nie obchodzi.
- **Narzędzia systemowe**: wykonanie komend wymaga jawnego uprawnienia zgodnego z rolą systemową; rozmowa nie jest równoznaczna z pozwoleniem na wykonanie.
- **Operacje nieodwracalne**: formatowanie, kasowanie danych, zmiany partycji i konfiguracji dostępu wymagają kontroli uprawnień oraz potwierdzenia.
- **Dane poufne**: klucze API, hasła i tokeny nie są zapisywane w repozytorium ani automatycznie przekazywane agentom.

## Stan implementacji

Adaptery `services/ai.py` i `services/openai_agents.py` nie mają dodatkowej warstwy filtrowania tematów. Ich komunikaty systemowe określają język i wymóg nieprzypisywania sobie niewykonanych działań. Odpowiedzi z zewnętrznych API pozostają zależne od dostawcy.

Dokument opisuje politykę projektu; nie znosi zasad bezpieczeństwa zewnętrznych usług i nie udziela agentom automatycznych uprawnień root.
