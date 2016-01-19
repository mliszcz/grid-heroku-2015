# Budowa aplikacji dla Heroku

Ten rozdział przedstawia proces budowy przykładowej aplikacji opartej o model
klient-serwer. Aplikacja zostanie uruchomiona na platformie Heroku.

## Ograniczenia

Ze względu na specyfikę platformy, docelowe aplikacje to głównie:
* aplikacje webowe
* usługi typu web-servce

Wynika to z wielu ograniczeń nałożonych przez autorów platformy Heroku,
między innymi:
* brak konfiguracji portów TCP (dostępne 80, 443)
* jeden proces *per dyno*
* brak możliwości komunikacji między procesami
* brak dostępu do systemu plików

Oferowana funkcjonalność jest jednak wystarczająca do hostowania aplikacji
opartych o model mikroserwisów, który staje się coraz bardziej popularny.

## Wybór technologii

Heroku wspiera najpopularniejsze frameworki dla aplikacji webowych, są to
między innymi:
* Java, Scala, Clojure - dowolny kontener servletów
* Ruby - Rails
* Python - Django
* Javascript - Node.js
* Go

Do implementacji przykładowej aplikacji wybraliśmy język Java oraz lekki
web-framework [Spark](http://sparkjava.com) (NIE ten od Apache!)

Framework dystrybuowany jest z dołączonym kontenerem Jetty, co pozwala na
uruchomienie aplikacji na platformie Heroku przy minimalnej konfiguracji.

## Implementacja serwera

W celu zademonstrowania programowania dla platformy Heroku, zbudujemy prosty
web-service udostępniający funckjonalność **całkowania numerycznego** metodą
prostokątów.

1. Zaczynamy od stworzenia pustego projektu. Zależności i proces budowania
   najlepiej kontrolować przy użyciu Maven-a lub podobnego narzędzia.
   W przypadki Maven-a dołączamy do projektu zależność

  ```xml
  <dependency>
    <groupId>com.sparkjava</groupId>
    <artifactId>spark-core</artifactId>
    <version>2.3</version>
  </dependency>
  ```

1. Spark to prosty framework, którego API ma formę *Domain-Specific-Language*
   dla serwerów aplikacji. Wszystkie potrzebne funkcje to statyczne funkcje w
   obiekcie `spark.Spark`. Wymagana jest Java 8.

    Dodajemy do projektu klasę z metodą `static void main(String[])` w której
    umieszczamy obsługę zapytania HTTP GET:

    ```java
    import static spark.Spark.*;

    public static void main(String[] args) {

      get("/", (req, res) -> {
        return "Hello world!";
      }

    }
    ```

1. Komiplujemy i uruchamiamy proram. Zostaje uruchomony serwer Jetty. W
   przeglądarce internetowej przechodzimy do adresu

  ```
  http://localhost:4567/
  ```

  Spark wyświetlił napis zwrócony z metody obsługującej zapytanie jako HTML
  (jest to domyślny *content-type* jeżeli nie podamy własnego).

1. Zmienimy teraz port na którym nasłuchuje serwer. Służy do tego funkcja
   `port(int)`. Docelowo program będzie uruchomiony na platformie Heroku.
   **Heroku udostępnia port dla aplikacji w zmiennej środowiskowej ``$PORT`**.
   Użyjmy więc tej wartości, a kiedy jest niedostępna, wybierzmy `8080`.

    ```java
    int listenPort = Optional
            .ofNullable(System.getenv("PORT"))
            .map(Integer::valueOf)
            .orElse(8080);

    port(listenPort);
    ```

    Powyższy kod należy umieścić przed pierwszym wywołaniem `get(...)`.

1. Dodajmy API pozwalające na całkowanie funkcji. Parametry będziemy pobierać
   z *query-string* zapytania GET. Zapytania HTTP to jedyna możliwość
   interakcji a aplikacjami w Heroku.

   Zakładamy następujący interfejs naszego web-service:

    ```
    http(s)://<endpoint>/integrate?function=sin(x)&from=0&to=1&steps=1000
    ```

    Web-service powinien zwrócić obiekt typu JSON (w tym wypadku liczbę).
    Musimy pamiętać o ustawieniu odpowiedniego nagłówka `content-type`.
    W tak prostym przypadku konwersja nastąpi automatycznie.

    ```java
    get("/integrate", (req, res) -> {

        String function = req.queryParams("function");
        String from = req.queryParams("from");
        String to = req.queryParams("to");
        String steps = req.queryParams("steps");

        double integral = integrateRectangles(parseFunction(function),
                                              Double.valueOf(from),
                                              Double.valueOf(to),
                                              Long.valueOf(steps));

         res.type("application/json; charset=utf-8");
         return integral;
    });
    ```

    Do zaimplementowania pozostały dwie funkcje:
      * `parseFunction` - konwertująca `String` na `Function<Double,Double>`;
      * `integrateRectangles` - dokonująca całkowania numerycznego zadanej
        funkcji na danym przedziale.

1. Do parsowania wyrażenia arytmetycznego wykorzystamy bibliotekę
   [exp4j](http://www.objecthunter.net/exp4j/). Dołączamy zależność i
   implementujemy prostą funkcję zamieniającą `String` na
   `Function<Double,Double>`:

    ```xml
    <dependency>
      <groupId>net.objecthunter</groupId>
      <artifactId>exp4j</artifactId>
      <version>0.4.5</version>
    </dependency>
    ```

    ```java
    private static Function<Double, Double> parseFunction(String expression) {
        Expression expr = new ExpressionBuilder(expression)
                .variables("pi", "e", "PI", "E", "x")
                .build()
                .setVariable("pi", Math.PI)
                .setVariable("e", Math.E)
                .setVariable("PI", Math.PI)
                .setVariable("E", Math.E);
        return x -> expr.setVariable("x", x).evaluate();
    }
    ```

1. Implementujemy całkowanie metodą prostokątów:

    ```java
    private static double integrateRectangles(Function<Double, Double> function,
                                              double from,
                                              double to,
                                              long steps) {
        double dx = (to - from) / steps;
        return LongStream.range(0, steps)
                .parallel()
                .mapToDouble(i -> dx * function.apply(from + i*dx + 0.5*dx))
                .sum();
    }
    ```

1. Uruchamiamy serwer i sprawdzamy działanie aplikacji (wpisując odpowiedni
   URL w pasku adresu przeglądarki). Przejdziemy teraz do uruchomienia
   aplikacji w chmurze Heroku.


## Uruchomienie na platformie Heroku

1. Zakładamy darmowe konto na platformie Heroku:

   ```
   https://signup.heroku.com/
   ```

1. Instalujemy pakiet *Heroku Toolbelt* w wersji dla naszego systemu
   operacyjnego:

   ```
   https://toolbelt.heroku.com/
   ```

1. Jeżeli poprawnie zainstalowaliśmy *Toolbelt*, przechodzimy do katalogu
   naszego projektu i wydajemy polecenie:

   ```
   $ git init // jeżeli jeszcze nie utworzyliśmy repozytorium
   $ heroku create
   ```

   Zostaniemy zapytani o dane do logowania podane przy rejestracji a następnie
   do repozytorium zostanie dodany *remote* on nazwie `heroku`. Zobaczymy
   komunikat:

   ```
   Creating tranquil-journey-6372... done, stack is cedar-14
   http://tranquil-journey-6372.herokuapp.com/ | https://git.heroku.com/tranquil-journey-6372.git
   Git remote heroku added
   ```

   **Zapamiętujemy adres HTTP naszej aplikacji.** (można go później odczytać
   z panelu administractyjnego platformy).

   Umieszczamy nasz kod w repozytorium Heroku:

   ```
   $ git push heroku master
   ```

   Aplikacja zostanie wysłana i zbudowana w Heroku. Testujemy działanie w
   przeglądarce:

   ```
   http://tranquil-journey-6372.herokuapp.com/integrate?function=sin(x)&from=0&to=1&steps=1000
   ```

   **W razie problemów należy upewnić się czy został uruchomiony proces WWW.**
   W katalogu aplikacji wpisujemy:

   ```
   $ heroku ps
   === web (Free): java -cp target/classes:target/dependency/* Main
   web.1: up 2016/01/19 17:51:59 (~ 49m ago)
   ```

   Dyno można uruchomić następującym poleceniem:

   ```
   $ heroku scale web=1
   Scaling dynos... done, now running web at 1:Free.
   ```

   Aby wyłączyć aplikację wpisujemy:

   ```
   $ heroku scale web=0
   Scaling dynos... done, now running web at 0:Free.
   ```

## Implementacja klienta

Dla zaimplementowanego API możemy napisać prostą bibliotekę kliencką.
Przykład w języku Python:

```python
class HerokuServiceClient:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def integrate(self, function, rangeFrom, rangeTo, steps):
        query_string = urllib.urlencode({'function': function,
                                         'from': rangeFrom,
                                         'to': rangeTo,
                                         'steps': steps})
        url = "{}/integrate?{}".format(self.endpoint, query_string)
        return float(urllib2.urlopen(url).read())
```

Można jej użyć z dowolnego programu w Pythonie (na przykład w celu pomiarów
wydajności platformy Heroku).

```
client = HerokuServiceClient('http://tranquil-journey-6372.herokuapp.com')
integral = client.integrate('sin(x)', 0, 1, 100)
```

Dostarczona implementacja zawiera również intercejs CLI oraz proste GUI
webowe:

* CLI: [client/client.py](https://github.com/mliszcz/grid-heroku-2015/blob/master/client/client.py)
* GUI: [src/main/resources/public/index.html](https://github.com/mliszcz/grid-heroku-2015/blob/master/src/main/resources/public/index.html)

# Wyniki

Testy wydajnościowe zostały przeprowadzone w dwóch wariantach:
- testy wydajnościowe dla jednego wątku
- testy wydajności w przypadku wielu wątków

## Testy wydajnościowe dla jednego wątku

W tym teście sprawdzaliśmy wydajność maszyny Heroku w przypadku obliczeń wykonywanych na jednym wątku. 
Testowana była moc obliczeniowa pojedynczej maszyny, poprzez zwiększanie ilości kroków w zaimplementowanym algorytmie całkowania metodą prostokątów.
Testy przeprowadzone zostały dla stałej liczy zapytań (requests = 100)
Jak widać na załączonych wykresach, dla małej ilości kroków obliczenia wykonywane na Heroku zajmują znacznie więcej czasu, jednakże można zauważyć, że Heroku jest wolniejsze o pewną stała ilość czasu (okolo 30s). Te 30s to prawdopodobnie czas potrzebny na przesłanie danych i zainicializowanie maszyny. Dla dużej ilości kroków (>1000000) Heroku wypada zauważalnie lepiej.

## Testy wydajnościowe w przypadku wielu wątków

W teście tym sprawdzalismy jak zwiększenie ilości wykorzystywanych wątków wpłynie na wydajność obliczeniową maszyny Heroku.
Obliczenia zostały przeprowadzone dla stałej wielkości problemu (steps = 100) oraz dla stałej liczby zapytań (requests = 100).
Jak widać zwiększanie ilości wykorzystywanych wątków znacząco nie wpływa na wydajność maszyny Heroku. Da się jedynie zauważyć zwiększenie odchylenia standardowego wraz, ze zwiększeniem ilości wykorzystywanch wątków.

# Odnośniki

* https://en.wikipedia.org/wiki/Rectangle_method
* https://devcenter.heroku.com/articles/runtime-principles
* https://devcenter.heroku.com/articles/limits
* https://devcenter.heroku.com/articles/heroku-postgres-plans
