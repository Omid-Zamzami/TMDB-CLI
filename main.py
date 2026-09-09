import argparse


def parse_argument():
    parser = argparse.ArgumentParser(description="CLI tool for fetching user's movie type from TMDB.")

    parser.add_argument(
        "-t",
        "--type",
        type=str.lower,
        choices=["playing", "popular", "top", "upcoming"],
        default="top",
        help="Type of movies based on user's choice. (Default: top)"
    )

    return parser.parse_args()


def tmdb():
    arg = parse_argument()
    print(f"user's choice: {arg.type}")


if __name__ == "__main__":
    tmdb()