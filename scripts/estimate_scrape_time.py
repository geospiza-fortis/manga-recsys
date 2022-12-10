"""Do a small regression to estimate the time it takes to scrape a page."""
import time
from argparse import ArgumentParser

import pandas as pd
from sklearn.linear_model import LinearRegression


def count_lines(path):
    """Count the number of lines in a file."""
    with open(path) as f:
        return sum(1 for _ in f)


def unix_to_iso(unix):
    """Convert unix time to ISO format."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix))


def fit_model(history, times):
    """Fit a model to the history of counts and times."""
    X = pd.Series(history).values.reshape(-1, 1)
    y = pd.Series(times).values
    X = X - X[0][0]
    y = y - y[0]
    model = LinearRegression()
    model.fit(X, y)
    return model


def predict(model, history, times, total):
    x0 = history[0]
    y0 = times[0]
    pred = model.predict([[total - x0]])[0]
    return pred + y0


def main():
    parser = ArgumentParser()
    parser.add_argument("total", type=int, help="Total number of items to scrape.")
    parser.add_argument("path", help="Path to CSV file with scraped data.")
    parser.add_argument(
        "--polling-interval",
        type=float,
        default=15,
        help="Time to wait between requests.",
    )
    parser.add_argument(
        "--model-interval",
        type=float,
        default=60,
        help="Time to wait between requests.",
    )
    args = parser.parse_args()

    # Estimate the time it takes to scrape a page
    model_last_fit = time.time()
    model = None
    total = args.total

    history = [count_lines(args.path)]
    times = [time.time()]
    while history[-1] < total:
        # collect some data
        time.sleep(args.polling_interval)
        current = count_lines(args.path)

        ts = time.time()
        rate = (current - history[0]) / (ts - times[0])
        if model:
            pred = predict(model, history, times, total)
        print(
            "\t".join(
                [
                    unix_to_iso(ts),
                    f"current: {current}",
                    f"total: {total}",
                    f"rate: {rate:.2f}",
                    *(
                        [f"eta: {(pred - ts)/60:.2f} m, {(pred - ts)/3600:.2f} h"]
                        if model
                        else []
                    ),
                ]
            )
        )
        history.append(current)
        # keep deltas between counts
        times.append(time.time())

        # limit history to 1000 items
        history = history[-1000:]
        times = times[-1000:]

        # fit a model every minute
        if time.time() - model_last_fit > args.model_interval and len(history) > 3:
            model = fit_model(history, times)
            model_last_fit = time.time()


if __name__ == "__main__":
    main()
