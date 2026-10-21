"""
Usage:
    python run.py --step all
    python run.py --step fetch
    python run.py --step details
    python run.py --step merge
    python run.py --step clean
    python run.py --step feature
    python run.py --step match
    python run.py --step recommend
"""

import argparse
import time

from src.scraper.fetch_jobs import main as fetch_jobs
from src.scraper.fetch_details import main as fetch_details
from src.preprocessing.merge_data import main as merge_data
from src.preprocessing.clean_data import main as clean_data



PIPELINE = {
    "fetch": fetch_jobs,
    "details": fetch_details,
    "merge": merge_data,
    "clean": clean_data,
}


def run_step(name: str, func):
    print("=" * 60)
    print(f"Running: {name}")
    print("=" * 60)

    start = time.perf_counter()

    try:
        func()

        elapsed = time.perf_counter() - start

        print(f"{name} completed ({elapsed:.2f} sec)\n")

    except Exception as e:
        print(f"{name} failed")
        print(e)
        raise


def run_all():

    for name, func in PIPELINE.items():
        run_step(name, func)


def main():

    parser = argparse.ArgumentParser(
        description="Iran Job Market Analysis Pipeline"
    )

    parser.add_argument(
        "--step",
        default="all",
        choices=["all", *PIPELINE.keys()],
        help="Run a specific pipeline step.",
    )

    args = parser.parse_args()

    total_start = time.perf_counter()

    print("\n")
    print("=" * 60)
    print("Iran Job Market Analysis")
    print("=" * 60)

    if args.step == "all":
        run_all()
    else:
        run_step(args.step, PIPELINE[args.step])

    total_elapsed = time.perf_counter() - total_start

    print("=" * 60)
    print(f"Pipeline Finished Successfully ({total_elapsed:.2f} sec)")
    print("=" * 60)


if __name__ == "__main__":
    main()