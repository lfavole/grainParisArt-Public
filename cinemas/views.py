from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Movie

# Create your views here.


def home(request: HttpRequest):
    """Home page."""
    try:
        delta = int(request.GET.get("delta", 0))
    except ValueError:
        delta = 0

    if delta > 6:
        delta = 6
    if delta < 0:
        delta = 0

    dates = []

    theater_locations = []
    for theater in settings.THEATERS:
        theater_locations.append(
            {
                "coordinates": [theater.longitude, theater.latitude],
                "description": theater.name,
            }
        )

    today = datetime.today()
    for i in range(0, 7):
        dates.append(today + timedelta(i))

    movies = (
        Movie.objects
        .prefetch_related("cast", "genres", "showtime_set")
        .select_related("director")
        .annotate(showtime_count=Count("showtime", filter=Q(showtime__start_time__date=dates[delta])))
        .filter(showtime_count__gt=0)
    )

    return render(
        request,
        "index.html",
        {
            "page_actuelle": "home",
            "films": movies,
            "dates": enumerate(dates),
            "current_date": dates[delta],
            "theater_locations": theater_locations,
            "website_title": settings.WEBSITE_TITLE,
            "mapbox_token": settings.MAPBOX_TOKEN,
        },
    )


def health(_request):
    """Health check."""
    return HttpResponse("OK", content_type="text/plain")
