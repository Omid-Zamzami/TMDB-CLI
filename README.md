# TMDB CLI

A Python command-line application for exploring movie data from [The Movie Database (TMDB)](https://www.themoviedb.org/) using the TMDB API.

## Features

- Fetch **Now Playing**, **Popular**, **Top Rated**, and **Upcoming** movies.
- Select the movie category with a command-line option.
- Use **Top Rated** movies as the default category.
- Authenticate securely with a TMDB API Read Access Token stored in an environment variable.
- Display movie title, release date, average vote, vote count, popularity, and overview.
- Handle common network, HTTP, timeout, and JSON parsing errors gracefully.
- Includes automated unit tests with `pytest`.

## Requirements

- Python 3.9 or newer
- A TMDB account and API Read Access Token
- Internet access when running the application against the TMDB API

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Omid-Zamzami/TMDB-CLI.git
cd TMDB-CLI
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The application reads the TMDB API Read Access Token from the `TMDB_API_TOKEN` environment variable.

Create a local `.env` file in the project root:

```env
TMDB_API_TOKEN=your_tmdb_read_access_token
```

Do not commit your `.env` file or expose your API token publicly.

The repository includes `.env.example` as a template for the required environment variable. The `.gitignore` file excludes `.env` and common local development files from Git. 

## Usage

Run the application without arguments to use the default **Top Rated** category:

```bash
python main.py
```

Select a category with either the short or long option:

```bash
python main.py --type popular
```

```bash
python main.py -t popular
```

### Available movie types

| CLI value | TMDB category |
|---|---|
| `playing` | Now Playing |
| `popular` | Popular |
| `top` | Top Rated |
| `upcoming` | Upcoming |

Examples:

```bash
python main.py --type playing
python main.py --type popular
python main.py --type top
python main.py --type upcoming
```

The `--type` argument is case-insensitive, so values such as `POPULAR` are converted to lowercase automatically.

## Example Output

```text
Displaying movies:

1. Title: Example Movie
    Release date: 2026-01-01
    Average vote: 8.5
    Vote count: 1000
    Popularity: 123.45
    Overview: An example movie.
```

The actual movie data displayed by the application is retrieved from TMDB and may change over time.

## Testing

The project uses `pytest` for automated testing.

Run all tests:

```bash
pytest -v
```

The test suite covers:

- Command-line argument parsing
- Short and long CLI options
- Default movie type
- Case conversion
- Invalid movie types
- TMDB endpoint mapping
- API request parameters and authentication header
- Missing API results
- Timeout errors
- Connection errors
- HTTP errors
- General request errors
- Invalid JSON responses
- Movie output formatting
- Empty movie results
- Missing movie fields
- Missing API token
- The main application workflow

The tests mock network requests, so they do not require a real TMDB API request or API token.

## Project Structure

```text
TMDB-CLI/
├── .env.example
├── .gitignore
├── LICENSE
├── main.py
├── requirements.txt
└── test_main.py
```

## Dependencies

The project uses the following Python packages:

- `requests` — HTTP requests to the TMDB API
- `python-dotenv` — loading environment variables from `.env`
- `pytest` — automated testing

See `requirements.txt` for the project dependency requirements.

## Error Handling

The application handles common failures without crashing unexpectedly, including:

- Missing TMDB API token
- Request timeout
- Connection failure
- HTTP errors such as unauthorized requests
- Other request-related errors
- Invalid JSON responses
- Empty movie results

When an error occurs, the application displays an informative message in the terminal.

## Security

API credentials should never be hard-coded into the source code or committed to GitHub.

This project stores the TMDB API Read Access Token in the `TMDB_API_TOKEN` environment variable and uses a local `.env` file for development. The `.env` file is excluded through `.gitignore`.

## TMDB Attribution

This project uses the TMDB API but is not endorsed or certified by TMDB.

Movie data and related information are provided by TMDB.

For TMDB API documentation, visit the [official TMDB developer documentation](https://developer.themoviedb.org/docs).

## License

This project is licensed under the terms of the license included in the repository's `LICENSE` file.

## Author

**Omid Zamzami**

GitHub: [Omid-Zamzami](https://github.com/Omid-Zamzami)

Repository: [TMDB-CLI](https://github.com/Omid-Zamzami/TMDB-CLI)
