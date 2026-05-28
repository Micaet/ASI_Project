# Uzasadnienie wyboru technologii

## Warstwa ingestion

### httpx

Asynchroniczny klient HTTP dla Pythona. Wybrany zamiast standardowej biblioteki requests, ponieważ obsługuje async/await natywnie. Dzięki temu scheduler nie blokuje się, gdy jedno z API odpowiada wolno.

### APScheduler

Scheduler uruchamiający joby cykliczne (polling ISS co 30s, RocketLauch.Live co 1h) wewnątrz procesu Pythona, bez potrzeby doinstalowywania crona.

## Warstwa przetwarzania

### Pydantic 

Biblioteka do walidacji i serializacji danych. Każda odpowiedź z zewnętrznego API przechodzi przez model Pydantic, który sprawdza typy, zakresy wartości i konwertuje formaty. Kluczową zaletą jest to żę te same modele Pydantic są reużywane w FastAPI jako schematy request/response, co eliminuje duplikację definicji danych.

## Warstwa bazy danych

### PostgreSQL

Darmowa Relacyjna baza danych. Wybrana zamiast SQLite, ponieważ SQLite nie obsługuje współbieżnego dostępu. PostgreSQL oferuje także natywne typy przydatne w projekcie: TIMESTAMPTZ (czas z timezone, kluczowy przy danych UTC z API), JSONB (opcjonalne przechowywanie surowych odpowiedzi API). Dodatkowo PostgreSQL jest dostępny jako lekki obraz Dockerowy (postgres:16-alpine).

### SQLAlchemy

ORM (Object-Relational Mapping) mapujący tabele na klasy Pythona. Wybrany, ponieważ:

1. Schemat bazy jest zdefiniowany w jednym miejscu (modele Pythonowe), co eliminuje ryzyko rozsynchronizowania kodu z bazą.
2. Integruje się z Pydantic (konwersja modeli).

## Warstwa backend

### FastAPI

Framework do budowy REST API

1. Automatyczna generacja dokumentacji Swagger
2. Natywna integracja z Pydantic (response_model w endpoincie = automatyczna walidacja i serializacja).
3. Wbudowany TestClient do testów jednostkowych endpointów.

## Warstwa frontend

### Leaflet.js

Biblioteka JavaScript do interaktywnych map.

## Zewnętrzne API

### WhereTheISS.at

Darmowe API zwracające aktualną pozycję ISS (latitude, longitude, altitude, velocity). Nie wymaga klucza API ani rejestracji. Alternatywa Open Notify (api.open-notify.org) zwraca tylko latitude i longitude bez dodatkowych parametrów, ale jest używany jako fallback w przypadku niedostępności WhereTheISS.

### RocketLaunch.Live

Darmowe API dostarczające dane o nadchodzących startach rakietowych, wraz z informacjami o dostawcy, pojeździe startowym i szczegółach misji. Odpowiedzi mają czytelną, płaską strukturę JSON, którą łatwo zmapować na model Pydantic (RocketLaunch) i tabelę spacex_launches. 

### Nominatim (OpenStreetMap)

API reverse geocoding zamieniające współrzędne geograficzne na nazwę kraju. Używane do wzbogacenia danych ISS o informację, nad jakim krajem aktualnie przelatuje stacja. Limit 1 request/s, darmowe i nie wymaga rejestracji.

## Testowanie

### pytest

Standardowy framework testowy w Pythonie. Wybrany zamiast wbudowanego unittest ze względu na prostszą składnię (zwykłe funkcje zamiast klas), system fixtures. FastAPI ma wbudowany TestClient kompatybilny z pytest.

### locust

Narzędzie do testów wydajnościowych. Scenariusze testowe pisze się w Pythonie, co jest spójne z resztą projektu. Generuje raporty HTML z metrykami (latency, throughput, percentyle).

## Logowanie

### logging (moduł standardowy)

Wbudowany moduł Pythona do logowania. Nie wymaga dodatkowych zależności. Skonfigurowany z formatem zawierającym timestamp, poziom logu, nazwę modułu i treść komunikatu.
