"""
Usage:
    python run.py --step all
    python run.py --step all --update     
    python run.py --step fetch --update
    python run.py --step details
    python run.py --step merge
    python run.py --step clean
"""

import argparse
import time
from functools import partial

from src.scraper.fetch_jobs import main as fetch_jobs
from src.scraper.fetch_details import main as fetch_details
from src.preprocessing.merge_data import main as merge_data
from src.preprocessing.clean_data import main as clean_data


def build_pipeline(update=False):
    return {
        "fetch": partial(fetch_jobs, update=update),
        "details": fetch_details,
        "merge": merge_data,
        "clean": clean_data,
    }


def run_step(name, func):
    print("=" * 60)
    print(f"Running: {name}")
    print("=" * 60)

    start = time.perf_counter()

    try:
        func()
        print(f"{name} completed ({time.perf_counter() - start:.2f} sec)\n")
    except Exception as e:
        print(f"{name} failed")
        print(e)
        raise


def main():
    parser = argparse.ArgumentParser(description="Iran Job Market Analysis Pipeline")

    parser.add_argument(
        "--step",
        default="all",
        choices=["all", *build_pipeline().keys()],
        help="Run a specific pipeline step.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Fetch only new job posts for already-scraped keywords.",
    )

    args = parser.parse_args()
    pipeline = build_pipeline(update=args.update)

    total_start = time.perf_counter()

    print("\n" + "=" * 60)
    print("Iran Job Market Analysis")
    print("=" * 60)

    steps = pipeline if args.step == "all" else {args.step: pipeline[args.step]}
    for name, func in steps.items():
        run_step(name, func)

    print("=" * 60)
    print(f"Pipeline Finished Successfully ({time.perf_counter() - total_start:.2f} sec)")
    print("=" * 60)


if __name__ == "__main__":
    main()
