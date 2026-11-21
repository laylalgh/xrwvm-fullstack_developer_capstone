import json
from datetime import date
from urllib.parse import quote

import requests
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .models import CarModel
from .restapis import analyze_review_sentiments, get_request, post_review


def error(message, status):
    return JsonResponse({"status": status, "message": message}, status=status)


def read_body(request):
    try:
        data = json.loads(request.body)
        return data if isinstance(data, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return {}


@require_POST
def login_user(request):
    data = read_body(request)
    username, password = data.get("userName"), data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return error("Username and password are required", 400)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return error("Invalid credentials", 401)
    login(request, user)
    return JsonResponse({"userName": user.username, "status": "Authenticated",
                         "firstName": user.first_name, "lastName": user.last_name})


@require_POST
def logout_request(request):
    logout(request)
    return JsonResponse({"status": "Logged out"})


@require_POST
def registration(request):
    data = read_body(request)
    fields = ["userName", "firstName", "lastName", "email", "password"]
    if not all(isinstance(data.get(field), str) and data[field].strip() for field in fields):
        return error("All five fields are required", 400)
    user = get_user_model()(username=data["userName"].strip(), first_name=data["firstName"],
                            last_name=data["lastName"], email=data["email"].strip())
    try:
        validate_email(user.email)
        user.full_clean(exclude=["password"], validate_unique=False)
        validate_password(data["password"], user)
        user.set_password(data["password"])
        user.save()
    except ValidationError as exc:
        return error(" ".join(exc.messages), 400)
    except IntegrityError:
        return error("Username already exists", 409)
    login(request, user)
    return JsonResponse({"userName": user.username, "status": "Authenticated"})


def dealer_response(key, endpoint):
    try:
        return JsonResponse({"status": 200, key: get_request(endpoint)})
    except (requests.RequestException, ValueError):
        return error("Dealership service unavailable", 502)


@require_GET
def get_dealerships(request, state=None):
    endpoint = f"fetchDealers/{quote(state, safe='')}" if state else "fetchDealers"
    return dealer_response("dealers", endpoint)


@require_GET
def get_dealer_details(request, dealer_id):
    return dealer_response("dealer", f"fetchDealer/{dealer_id}")


@require_GET
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
        for review in reviews:
            if not review.get("sentiment"):
                review.update(analyze_review_sentiments(review["review"]))
        return JsonResponse({"status": 200, "reviews": reviews})
    except (requests.RequestException, ValueError):
        return error("Review service unavailable", 502)


@require_GET
def get_cars(request):
    models = CarModel.objects.select_related("car_make").order_by("car_make__name", "name", "year")
    return JsonResponse({"CarModels": [
        {"CarMake": car.car_make.name, "CarModel": car.name, "year": car.year, "type": car.type}
        for car in models
    ]})


@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return error("Login required", 401)
    data = read_body(request)
    review = data.get("review")
    if not isinstance(review, str) or not review.strip() or len(review) > 4000:
        return error("Enter a review of 1–4000 characters", 400)
    try:
        dealer_id = int(data["dealership"])
        year = int(data["car_year"])
        purchased = date.fromisoformat(data["purchase_date"])
        make, model = data["car_make"].strip(), data["car_model"].strip()
        if not make or not model or not 1886 <= year <= date.today().year + 1:
            raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        return error("A dealer, car, year and purchase date are required", 400)
    try:
        if not get_request(f"fetchDealer/{dealer_id}"):
            return error("Dealer not found", 404)
        response = post_review({
            "name": request.user.get_full_name() or request.user.username,
            "dealership": dealer_id, "review": review.strip(), "purchase": True,
            "purchase_date": purchased.isoformat(), "car_make": make,
            "car_model": model, "car_year": year,
        })
        return JsonResponse({"status": 200, "review": response})
    except (requests.RequestException, ValueError):
        return error("Review service unavailable", 502)
