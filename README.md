# Projekt_informatyka_python
Autor: Miłosz Sobczak 
Numer indeksu: 203969
Wydział: EiA
Kierunek: Automatyka, robotyka i systemy sterowania
Opis Projektu:
Aplikacja symuluje przemysłową linię dozowania i podgrzewania cieczy. Została napisana w języku Python (PyQt5) z wykorzystaniem architektury obiektowej, co pozwala na niezależne zarządzanie logiką procesową i wizualizacją.

Kluczowe Funkcje
Wizualizacja: Dynamiczny podgląd poziomów, przepływów i zmian temperatury (kodowanie kolorami).

Logika Procesowa: Automatyczny transport produktu do magazynu dopiero po osiągnięciu temperatury technologicznej (>45°C).

Modele Fizyczne: Implementacja bilansu masy (ciecz ubywa ze źródła podczas pompowania) oraz bilansu cieplnego (mieszanie temperatur w magazynie).

Zarządzanie Danymi: Dedykowany ekran raportów z tabelą parametrów i systemem alarmów przepełnienia.

Instrukcja
Dozowanie: Przesuń suwak zasilania, aby wlać ciecz do układu.

Nagrzewanie: Ustaw Setpoint temperatury dla reaktorów.

Monitoring: Śledź postępy na schemacie lub przełącz na kartę raportów, aby sprawdzić precyzyjne dane.
