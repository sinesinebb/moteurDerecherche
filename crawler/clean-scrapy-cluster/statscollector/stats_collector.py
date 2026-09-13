import os
import sys
import time
import argparse

from stats_collector import StatsCollector


def main():
    # Debug environment
    print("DEBUG: Starting stats_collector with environment variables:")
    for var in ("REDIS_HOST", "REDIS_PORT", "REDIS_KEY", "WINDOW"):  # extend as needed
        print(f"  {var}={os.getenv(var)}")
    sys.stdout.flush()

    # Read configuration from environment
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_key = os.getenv("REDIS_KEY", "crawler_stats")
    window_size = int(os.getenv("WINDOW", 60))

    parser = argparse.ArgumentParser(description="Stats collector for crawler metrics.")
    parser.add_argument(
        '-k', '--key', default=redis_key,
        help='Redis key for the rolling counter'
    )
    parser.add_argument(
        '-w', '--window', type=int, default=window_size,
        help='Time window in seconds for the rolling counter'
    )
    args = parser.parse_args()

    # Initialize rolling window counter
    counter = StatsCollector.get_rolling_time_window(
        host=redis_host, port=redis_port,
        key=args.key, window=args.window
    )

    print('Stats Collector started')
    sys.stdout.flush()
    try:
        while True:
            counter.increment()
            current = counter.value()
            print(f'Current count for key "{args.key}": {current}')
            sys.stdout.flush()
            time.sleep(5)
    except KeyboardInterrupt:
        print('Stats Collector shutting down')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
