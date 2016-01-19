# Heroku - wprowadzenie

Heroku to platforma cloudowa udostępniająca zasoby w modelu
*Platform-as-a-Service* (PaaS). Przeznczona jest głównie dla lekkich
aplikacji webowych. Wspiera kilka języków programowania i przeznaczonych
dla nich frameworków.

## Oprogramowanie

### Stacks

Aplikacje użytkownika są uruchamiane w **lekkich kontenreach** na którym
działa udostępniony przez Heroku system operacyjny.

Obraz systemu wraz z zainstalowanym podstawowym oprogramowaniem nosi nazwę
*stack*. Obecnie oficjalnie wspierany jest jeden, **Cedar-14 Stack** oparty
na systemie Ubuntu.

Więcej: <https://devcenter.heroku.com/articles/stack>

### Aplikacje użytkownika

Heroku wspiera przyjazny deweloperom model wdrażania aplikacji do chmury,
poprzez integrację z systemem kontroli wersji (Git).

Heroku jest dodany jako zdalne repozytorium (*remote* w terminologii Git-a)
w trakcie tworzenia projektu. Commit do tego repozytorium powoduje
zbudowanie i uruchomienie aplikacji przez Heroku.

Możliwe są również inne opcje wdrożenia, między innymi:
* integracja z GitHub-em
* integracja z Dropboxem

Szczegółowa instrukcja uruchomienia przykładowej aplikacji przedstawiona
jest w jednym z dalszych rozdziałów.

### Buildpacks

*Buildpack* to skrypt kontrolujący proces budowania aplikacji użytkownika.
Każdy *Buildpack* ma trzy zadania:
* określenie czy potrafi zbudować dany projekt  
  (na przykład wykrycie pliku *pom.xml*)
* zbudowanie projektu  
  (na przykład instalacja Maven-a i wykonanie `mvn package`)
* zwrócenie informacji do środowiska
  (zmiennne systemowe, itp.)

Heroku standardowo wspiera kilka języków programowania i odpowiednie narzędzia
do kompilacji napisanych w nich aplikacji, Przykładowo:
* Java (Maven)
* Scala (SBT)
* Python (Pip)
* ...

W przypadku gdy jakiś język nie jest wspierany, w Internecie można znaleźć
odpowiedni buildpack (przykładowo dla języka Erlang).

Więcej: <https://devcenter.heroku.com/articles/buildpack-api>

### Procfiles

W każdym repozytorium powinien znajdować się plik `Procfile`. Określa on sposób
w jaki Heroku uruchomi aplikację. Format:

```
typ-procesu: polecenie-do-uruchomienia
```

Przykładowo dla aplikacji Java:

```
web:    java -cp target/classes:target/dependency/* Main
```

**Typ procesu** ustawiony został na *web*. Oznacza to że proces będzie
otrzymywał ruch HTTP na porcie określontm przez zmienną środowiskową `$PORT`.
Za kierowanie ruchem i rozkład obciążenia między większą ilość instancji
aplikacji odpowiadają routery HTTP Heroku.

Inny typ procesu to *worker*, wykonujący obliczenia w tle.

Dodatkowo istnieją typy procesów uruchamiane na żądanie i kończone kiedy nie
są już potrzebne.

Więcej: <https://devcenter.heroku.com/articles/procfile>

### Slugs

> Terminology: A slug is a bundle of your source, fetched dependencies, the
  language runtime, and compiled/generated output of the build system -
  ready for execution.

Więcej: <https://devcenter.heroku.com/articles/slug-compiler>

## Kontenery aplikacji

Kontenery w których uruchamiane są aplikacje, noszą nazwę *Dyno*.
Różne typy *dyno* różnią się między sobą możliwościami skalowalności,
wydajnością, czasem aktywności oraz oczywiście ceną.

Plan darmowy (*Free*) pozwala na uruchomienie jednej instancji aplikacji,
która może działać 16 godzin w ciągu doby.

Oprócz tego dostępne są usługi:

* baza SQL Postgres - w wersji darmowej do 10'000 wierszy
* baza Redis

Szczegóły: <https://www.heroku.com/pricing>

## Dodatki

Heroku oferuje ogromną liczbę dodatków, które można aktywować dla aplikacji,
przykładowo:

* grafowa baza danych Neo4j
* integracja z Amazon S3
* monitoring aplikacji
* zbieranie logów
* usługi email / SMS
* full-text search
* generatory obciążenia  
  (stress testing)
* integracja z usługami autentykacji
* i wiele innych ...

Pełna lista dodatków: <https://elements.heroku.com/addons>
