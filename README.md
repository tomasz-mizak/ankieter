# Ankieter
Prosty interfejs konsolowy do przetwarzania danych ankiet, z sytemu USOS.

Funkcje
- Liczenie średniej dla wszystkich pracowników w wybranej ankiecie (zapis w pliku .csv)
- Liczenie średniej dla pojedyńczej osoby
-- wyszukiwanie ręczne osób z całego zbioru
-- filtrowanie po nazwisku

## Przed uruchomieniem
Pobieramy Instant Client od Oracle, oraz umieszczamy go w katalogu ```C:\``` pod nazwą ```instantclient```.

<u>Program był tworzony na wersję 21.06, dlatego tylko tę wersję zalecam do pobrania.</u>

<a href="https://www.oracle.com/pl/database/technologies/instant-client/downloads.html" target="_blank">Tutaj pobierzesz <b>aktualną</b> wersję - Oracle Instant Client Downloads</a>

## Konfiguracja
W pliku .env zawarta jest konfiguracja programu

####<b>Pola obowiązkowe</b>
```
IPA=(adres ip)
PORT=(port)
DBN=(nazwa bazy/nazwa usługi)
```
####<b>Pola dodatkowe</b>
Pola dodatkowe używamy w sytuacji częstego korzystania z programu, głównym celem jest skrócenie dostępu do bazy, za każdym razem przy uruchomieniu programu należy podawać dane do logowania, owe pola pomijają logowanie. Oczywiście nie zachęcam do stosowania, gdyż jest to o wiele mniej bezpieczne.
```
USER=
PASSWORD=
```