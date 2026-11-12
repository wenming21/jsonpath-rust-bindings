"""Performance benchmarks, measured with pytest-codspeed.

Run locally with:

    pytest tests/test_benchmarks.py --codspeed

Without the ``--codspeed`` flag these run as regular tests.
"""

import copy

import pytest
from jsonpath_rust_bindings import Finder

SAMPLE = {
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
            },
        ],
        "bicycle": {"color": "red", "price": 19.95},
    },
    "expensive": 10,
}


def _make_large_store(n_books: int) -> dict:
    books = []
    for i in range(n_books):
        book = copy.deepcopy(SAMPLE["store"]["book"][i % 4])
        book["id"] = i
        book["price"] = round(5 + (i * 7) % 30 + 0.99, 2)
        book["tags"] = [f"tag{i % 10}", f"tag{i % 7}"]
        books.append(book)
    return {
        "store": {"book": books, "bicycle": {"color": "red", "price": 19.95}},
        "expensive": 10,
    }


LARGE = _make_large_store(1000)

SMALL_FINDER = Finder(SAMPLE)
LARGE_FINDER = Finder(LARGE)

SMALL_QUERIES = {
    "child_wildcard": "$.store.book[*].author",
    "filter_exists": "$..book[?(@.isbn)]",
    "recursive_descent": "$..author",
    "slice": "$..book[-2:]",
    "filter_compare": "$.store.book[?(@.price<10)]",
    "filter_root_ref": "$..book[?(@.price<=$.expensive)]",
    "all_nodes": "$..*",
    "regex_match": '$..book[?match(@.author, "(?i).*rees.*")]',
}

LARGE_QUERIES = {
    "child_wildcard": "$.store.book[*].author",
    "recursive_descent": "$..price",
    "filter_compare": "$.store.book[?(@.price<10)]",
    "filter_root_ref": "$..book[?(@.price<=$.expensive)]",
    "regex_match": '$..book[?match(@.author, "(?i).*rees.*")]',
}


@pytest.mark.benchmark
def test_finder_construct_small():
    Finder(SAMPLE)


@pytest.mark.benchmark
def test_finder_construct_large():
    Finder(LARGE)


@pytest.mark.benchmark
@pytest.mark.parametrize("query", SMALL_QUERIES.values(), ids=SMALL_QUERIES.keys())
def test_find_small(query):
    SMALL_FINDER.find(query)


@pytest.mark.benchmark
@pytest.mark.parametrize("query", SMALL_QUERIES.values(), ids=SMALL_QUERIES.keys())
def test_find_data_small(query):
    SMALL_FINDER.find_data(query)


@pytest.mark.benchmark
@pytest.mark.parametrize("query", SMALL_QUERIES.values(), ids=SMALL_QUERIES.keys())
def test_find_absolute_path_small(query):
    SMALL_FINDER.find_absolute_path(query)


@pytest.mark.benchmark
@pytest.mark.parametrize("query", LARGE_QUERIES.values(), ids=LARGE_QUERIES.keys())
def test_find_large(query):
    LARGE_FINDER.find(query)


@pytest.mark.benchmark
@pytest.mark.parametrize("query", LARGE_QUERIES.values(), ids=LARGE_QUERIES.keys())
def test_find_data_large(query):
    LARGE_FINDER.find_data(query)


@pytest.mark.benchmark
@pytest.mark.parametrize("query", LARGE_QUERIES.values(), ids=LARGE_QUERIES.keys())
def test_find_absolute_path_large(query):
    LARGE_FINDER.find_absolute_path(query)


@pytest.mark.benchmark
def test_construct_and_find_small():
    Finder(SAMPLE).find("$..book[?(@.price<=$.expensive)]")
