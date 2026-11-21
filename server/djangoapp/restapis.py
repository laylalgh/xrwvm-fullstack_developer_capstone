import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()
backend_url = os.getenv("backend_url", "http://localhost:3030").rstrip("/")
sentiment_analyzer_url = os.getenv("sentiment_analyzer_url", "http://localhost:5050").rstrip("/")


def get_json(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_request(endpoint):
    return get_json(f"{backend_url}/{endpoint}")


def analyze_review_sentiments(text):
    return get_json(f"{sentiment_analyzer_url}/analyze/{quote(text, safe='')}")


def post_review(data):
    response = requests.post(f"{backend_url}/insert_review", json=data, timeout=10)
    response.raise_for_status()
    return response.json()
