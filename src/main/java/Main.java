import static spark.Spark.get;
import static spark.Spark.port;
import static spark.Spark.staticFileLocation;

import java.util.Optional;
import java.util.function.Function;
import java.util.stream.LongStream;

import net.objecthunter.exp4j.Expression;
import net.objecthunter.exp4j.ExpressionBuilder;

public class Main {

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

    public static void main(String[] args) {

        staticFileLocation("/public");

        int listenPort = Optional
                .ofNullable(System.getenv("PORT"))
                .map(Integer::valueOf)
                .orElse(8080);

        port(listenPort);

        get("/integrate", (req, res) -> {

            String function = req.queryParams("function");
            String from = req.queryParams("from");
            String to = req.queryParams("to");
            String steps = req.queryParams("steps");

            double integral = integrateRectangles(parseFunction(function),
                                                  Double.valueOf(from),
                                                  Double.valueOf(to),
                                                  Long.valueOf(steps));

//            System.out.println(String.format(
//                    "Integral of %1$s over [%2$s,%3$s] is %4$f",
//                    function,
//                    from,
//                    to,
//                    integral));

            res.type("application/json; charset=utf-8");
            return integral;
        });
    }
}
