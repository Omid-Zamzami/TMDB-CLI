import argparse
import os
from dotenv import load_dotenv
import requests


def parse_argument():
    parser = argparse.ArgumentParser(
        description="CLI tool for fetching user's movie type from TMDB."
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str.lower,
        choices=["playing", "popular", "top", "upcoming"],
        help="Type of movies based on user's choice."
    )

    return parser.parse_args()


def fetch_movies(movie_type, access_token):
    movie_types = {
        "playing": "now_playing",
        "popular": "popular",
        "top": "top_rated",
        "upcoming": "upcoming"
    }

    try:
        endpoint = movie_types[movie_type]

        url = f"https://api.themoviedb.org/3/movie/{endpoint}"

        params = {
            'language': 'en-US',
            'page': 1
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url=url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])

        response.raise_for_status()

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


def display_movies(movies_list):
    if not movies_list:
        print("No movies found.")
        return
    
    print("\nDisplaying movies:\n")

    for index, item in enumerate(movies_list, start=1):
        title = item.get('title') or 'N/A'
        release_date = item.get('release_date') or 'N/A'
        vote_average = item.get('vote_average')
        vote_count = item.get('vote_count')
        overview = item.get('overview') or 'N/A'
        popularity = item.get('popularity')

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


def tmdb():
    arg = parse_argument()

    load_dotenv()

    api_token = os.getenv("TMDB_API_TOKEN")

    if not api_token:
        print("Error: TMDB API token was not found.")
        return

    movies_data = fetch_movies(arg.type, api_token)
    display_movies(movies_data)


if __name__ == "__main__":
    tmdb()