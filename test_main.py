import argparse
from typing import Any
from unittest.mock import Mock
import pytest
import requests
import main


# Tests for parse_argument

def test_parse_argument_with_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test parsing CLI arguments with the long option --type."""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "--type", "popular"]
    )

    args: argparse.Namespace = main.parse_argument()

    assert args.type == "popular"


def test_parse_argument_with_short_option(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test parsing CLI arguments with the short option -t."""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "-t", "upcoming"]
    )

    args: argparse.Namespace = main.parse_argument()

    assert args.type == "upcoming"


def test_parse_argument_converts_type_to_lowercase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that uppercase input is automatically converted to lowercase."""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "--type", "POPULAR"]
    )

    args: argparse.Namespace = main.parse_argument()

    assert args.type == "popular"


def test_parse_argument_uses_top_as_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that default option 'top' is selected when no flag is passed."""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py"]
    )

    args: argparse.Namespace = main.parse_argument()

    assert args.type == "top"


def test_parse_argument_rejects_invalid_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that passing an invalid movie type triggers SystemExit."""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "--type", "invalid"]
    )

    with pytest.raises(SystemExit):
        main.parse_argument()


# Tests for fetch_movies

@pytest.mark.parametrize(
    "movie_type, expected_endpoint",
    [
        ("playing", "now_playing"),
        ("popular", "popular"),
        ("top", "top_rated"),
        ("upcoming", "upcoming"),
    ],
)
def test_fetch_movies_uses_correct_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    movie_type: str,
    expected_endpoint: str,
) -> None:
    """Test that fetch_movies queries the appropriate endpoint for each movie type."""
    mock_response: Mock = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [{"title": "Example Movie"}]
    }

    mock_get: Mock = Mock(return_value=mock_response)
    monkeypatch.setattr(main.requests, "get", mock_get)

    result: list[dict[str, Any]] = main.fetch_movies(movie_type, "test-token")

    assert result == [{"title": "Example Movie"}]

    mock_get.assert_called_once_with(
        url=f"https://api.themoviedb.org/3/movie/{expected_endpoint}",
        params={
            "language": "en-US",
            "page": 1
        },
        headers={
            "Authorization": "Bearer test-token"
        },
        timeout=10
    )


def test_fetch_movies_returns_empty_list_when_results_are_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that fetch_movies returns an empty list if the results key is missing from JSON response."""
    mock_response: Mock = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    monkeypatch.setattr(
        main.requests,
        "get",
        Mock(return_value=mock_response)
    )

    result: list[dict[str, Any]] = main.fetch_movies("popular", "test-token")

    assert result == []


def test_fetch_movies_handles_timeout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test handling of request timeout exception during network call."""
    mock_get: Mock = Mock(
        side_effect=requests.exceptions.Timeout
    )

    monkeypatch.setattr(main.requests, "get", mock_get)

    result: list[dict[str, Any]] = main.fetch_movies("popular", "test-token")

    captured = capsys.readouterr()

    assert result == []
    assert "Request timed out" in captured.out


def test_fetch_movies_handles_connection_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test handling of network connection error exception."""
    mock_get: Mock = Mock(
        side_effect=requests.exceptions.ConnectionError
    )

    monkeypatch.setattr(main.requests, "get", mock_get)

    result: list[dict[str, Any]] = main.fetch_movies("popular", "test-token")

    captured = capsys.readouterr()

    assert result == []
    assert "Could not connect to TMDB" in captured.out


def test_fetch_movies_handles_http_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test handling of HTTP status errors (e.g., 401 Unauthorized)."""
    mock_response: Mock = Mock()
    mock_response.status_code = 401

    http_error: requests.exceptions.HTTPError = requests.exceptions.HTTPError(
        "401 Client Error: Unauthorized"
    )

    mock_response.raise_for_status.side_effect = http_error

    monkeypatch.setattr(
        main.requests,
        "get",
        Mock(return_value=mock_response)
    )

    result: list[dict[str, Any]] = main.fetch_movies("popular", "test-token")

    captured = capsys.readouterr()

    assert result == []
    assert "HTTP Error occurred" in captured.out


def test_fetch_movies_handles_request_exception(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test handling of general RequestException network errors."""
    mock_get: Mock = Mock(
        side_effect=requests.exceptions.RequestException(
            "Unexpected request error"
        )
    )

    monkeypatch.setattr(main.requests, "get", mock_get)

    result: list[dict[str, Any]] = main.fetch_movies("popular", "test-token")

    captured = capsys.readouterr()

    assert result == []
    assert "unexpected network error" in captured.out.lower()


def test_fetch_movies_handles_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test handling of invalid JSON responses from server."""
    mock_response: Mock = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError

    monkeypatch.setattr(
        main.requests,
        "get",
        Mock(return_value=mock_response)
    )

    result: list[dict[str, Any]] = main.fetch_movies("popular", "test-token")

    captured = capsys.readouterr()

    assert result == []
    assert "Failed to parse JSON response" in captured.out


# Tests for display_movies

def test_display_movies_prints_movie_information(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test formatting and printing of valid movie data."""
    movies: list[dict[str, Any]] = [
        {
            "title": "Example Movie",
            "release_date": "2026-01-01",
            "vote_average": 8.5,
            "vote_count": 1000,
            "overview": "An example movie.",
            "popularity": 123.45
        }
    ]

    main.display_movies(movies)

    captured = capsys.readouterr()

    assert "Displaying movies:" in captured.out
    assert "1. Title: Example Movie" in captured.out
    assert "Release date: 2026-01-01" in captured.out
    assert "Average vote: 8.5" in captured.out
    assert "Vote count: 1000" in captured.out
    assert "Popularity: 123.45" in captured.out
    assert "Overview: An example movie." in captured.out


def test_display_movies_handles_empty_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test message output when movie list is empty."""
    main.display_movies([])

    captured = capsys.readouterr()

    assert "No movies found." in captured.out


def test_display_movies_uses_na_for_missing_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test fallback value 'N/A' when movie details are missing or None."""
    movies: list[dict[str, Any]] = [
        {
            "title": "Example Movie",
            "release_date": "",
            "vote_average": None,
            "vote_count": None,
            "overview": "",
            "popularity": None
        }
    ]

    main.display_movies(movies)

    captured = capsys.readouterr()

    assert "Title: Example Movie" in captured.out
    assert "Release date: N/A" in captured.out
    assert "Average vote: N/A" in captured.out
    assert "Vote count: N/A" in captured.out
    assert "Overview: N/A" in captured.out
    assert "Popularity: N/A" in captured.out


# Tests for tmdb entry point

def test_tmdb_handles_missing_api_token(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test error message when TMDB_API_TOKEN is missing from environment variables."""
    mock_args: argparse.Namespace = argparse.Namespace(type="popular")

    monkeypatch.setattr(
        main,
        "parse_argument",
        Mock(return_value=mock_args)
    )

    monkeypatch.setattr(
        main.os,
        "getenv",
        Mock(return_value=None)
    )

    main.tmdb()

    captured = capsys.readouterr()

    assert "TMDB API token was not found." in captured.out


def test_tmdb_fetches_and_displays_movies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the complete successful execution workflow of the main tmdb function."""
    mock_args: argparse.Namespace = argparse.Namespace(type="popular")

    movies: list[dict[str, Any]] = [
        {
            "title": "Example Movie"
        }
    ]

    mock_parse_argument: Mock = Mock(return_value=mock_args)
    mock_fetch_movies: Mock = Mock(return_value=movies)
    mock_display_movies: Mock = Mock()

    monkeypatch.setattr(
        main,
        "parse_argument",
        mock_parse_argument
    )

    monkeypatch.setattr(
        main.os,
        "getenv",
        Mock(return_value="test-token")
    )

    monkeypatch.setattr(
        main,
        "fetch_movies",
        mock_fetch_movies
    )

    monkeypatch.setattr(
        main,
        "display_movies",
        mock_display_movies
    )

    main.tmdb()

    mock_fetch_movies.assert_called_once_with(
        "popular",
        "test-token"
    )

    mock_display_movies.assert_called_once_with(
        movies
    )