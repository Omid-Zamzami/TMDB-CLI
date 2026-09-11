import argparse
import os
from dotenv import load_dotenv
import requests
from typing import Any


def parse_argument() -> argparse.Namespace:
    """Parse and return command-line arguments."""

    # Initialize the argument parser with CLI description
    parser = argparse.ArgumentParser(
        description="CLI tool for fetching user's movie type from TMDB."
    )

    # Add optional movie type flag with allowed choices and standard default
    parser.add_argument(
        "-t",
        "--type",
        type=str.lower,
        choices=["playing", "popular", "top", "upcoming"],
        default="top",
        help="Type of movies based on user's choice. (Default: top)"
    )

    return parser.parse_args()


def fetch_movies(movie_type: str, access_token: str) -> list[dict[str, Any]]:
    """Fetch movies from TMDB based on the selected movie type."""

    # Map user-friendly movie types to TMDB API endpoints.
    movie_types: dict[str, str] = {
        "playing": "now_playing",
        "popular": "popular",
        "top": "top_rated",
        "upcoming": "upcoming"
    }

    try:
        endpoint: str = movie_types[movie_type]

        url: str = f"https://api.themoviedb.org/3/movie/{endpoint}"

        # Define query parameters for the API request.
        params: dict[str, Any] = {
            'language': 'en-US',
            'page': 1
        }

        # Use the TMDB API Read Access Token for authentication.
        headers: dict[str, str] = {
            "Authorization": f"Bearer {access_token}"
        }

        # Execute GET request to the TMDB API endpoint
        response: requests.Response = requests.get(url=url, params=params, headers=headers, timeout=10)

        # Check for successful response
        if response.status_code == 200:
            data: dict[str, Any] = response.json()
            return data.get('results', [])

        response.raise_for_status()

    # Handle network, HTTP, and JSON decoding errors
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please check your network and try again.")
        return []
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to TMDB. Please check your internet connection.")
        return []
    except requests.exceptions.HTTPError as error:
        print(f"HTTP Error occurred: {error}")
        return []
    except requests.exceptions.RequestException as error:
        print(f"An unexpected network error occurred: {error}")
        return []
    except ValueError:
        print("Error: Failed to parse JSON response from server.")
        return []


def display_movies(movies_list: list[dict[str, Any]]) -> None:
    """Display movie information in a readable format."""

    if not movies_list:
        print("No movies found.")
        return
    
    print("\nDisplaying movies:\n")

    # Iterate through the list of movies and print details
    for index, item in enumerate(movies_list, start=1):
        title: str = item.get('title') or 'N/A'
        release_date: str = item.get('release_date') or 'N/A'
        vote_average: float | str | None = item.get('vote_average')
        vote_count: int | str | None = item.get('vote_count')
        overview: str = item.get('overview') or 'N/A'
        popularity: float | str | None = item.get('popularity')

        # Use a fallback value when numeric fields are missing.
        if vote_average is None:
            vote_average = "N/A"
        if vote_count is None:
            vote_count = "N/A"
        if popularity is None:
            popularity = "N/A"

        print(f"{index}. Title: {title}")
        print(f"    Release date: {release_date}")
        print(f"    Average vote: {vote_average}")
        print(f"    Vote count: {vote_count}")
        print(f"    Popularity: {popularity}")
        print(f"    Overview: {overview}")


def tmdb() -> None:
    """Run the TMDB CLI application."""

    # Parse command line input arguments
    arg: argparse.Namespace = parse_argument()

    # Load environment variables from the .env file.
    load_dotenv()

    # Retrieve TMDB bearer API token from environment variables
    api_token: str | None = os.getenv("TMDB_API_TOKEN")

    if not api_token:
        print("Error: TMDB API token was not found.")
        return

    # Fetch movie data and render to terminal output
    movies_data: list[dict[str, Any]] = fetch_movies(arg.type, api_token)
    display_movies(movies_data)


if __name__ == "__main__":
    tmdb()