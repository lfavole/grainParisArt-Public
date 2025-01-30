from dataclasses import dataclass
from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import get_default_timezone
from django.utils.translation import gettext_lazy as _
import requests

from .fields import TheaterField
from .templatetags.format_runtime import format_runtime
from .utils import parse_runtime

# Create your models here.


class Actor(models.Model):
    """Actor model."""
    id = models.IntegerField(_("ID"), primary_key=True)
    first_name = models.CharField(_("First name"), blank=True, max_length=100)
    last_name = models.CharField(_("Last name"), blank=True, max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = _("actor")
        verbose_name_plural = _("actors")

    @classmethod
    def from_allocine(cls, data):
        """Create an `Actor` instance from Allocine data."""
        return cls(id=int(data["internalId"]), first_name=data["firstName"] or "", last_name=data["lastName"] or "")

    @classmethod
    def get_or_create_from_data(cls, data):
        """Get or create an `Actor` instance from Allocine data."""
        try:
            return cls.objects.get(id=int(data["internalId"]))
        except cls.DoesNotExist:
            ret = cls.from_allocine(data)
            ret.save()
            return ret


class Genre(models.Model):
    """Genre model."""
    id = models.IntegerField(_("ID"), primary_key=True)
    name = models.CharField(_("Name"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    @classmethod
    def from_allocine(cls, data):
        """Create a `Genre` instance from Allocine data."""
        return cls(id=int(data["id"]), name=data["translate"])

    @classmethod
    def get_or_create_from_data(cls, data):
        """Get or create a `Genre` instance from Allocine data."""
        try:
            return cls.objects.get(id=int(data["id"]))
        except cls.DoesNotExist:
            ret = cls.from_allocine(data)
            ret.save()
            return ret


class Movie(models.Model):
    """Movie model."""
    id = models.IntegerField(_("ID"), primary_key=True)
    title = models.CharField(_("Title"), max_length=255)
    runtime = models.IntegerField(_("Runtime"))
    synopsis = models.TextField(_("Synopsis"))
    genres = models.ManyToManyField("Genre", verbose_name=_("Genres"))
    want_to_see_count = models.IntegerField(_("Want to see count"))
    poster = models.URLField(_("Poster"), blank=True)
    cast = models.ManyToManyField("Actor", verbose_name=_("Cast"))
    director = models.ForeignKey(
        "Actor", verbose_name=_("Director"), related_name="main_movie_set", null=True, on_delete=models.CASCADE
    )

    @property
    def runtime_human(self):
        """Get the runtime in human-readable format."""
        return format_runtime(self.runtime)
    runtime_human.fget.short_description = _("Runtime")
    runtime_human.fget.admin_order_field = "runtime"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("movie")
        verbose_name_plural = _("movies")

    @classmethod
    def from_allocine(cls, data):
        """Create a `Movie` instance from Allocine data."""
        try:
            poster = data["poster"]["url"]
        except:
            poster = ""

        cast = []

        # Noms des acteurs
        for actor in data["cast"]["edges"]:
            if actor["node"]["actor"] == None:
                continue
            cast.append(Actor.get_or_create_from_data(actor["node"]["actor"]))

        # Nom du réalisateur
        if len(data["credits"]) == 0 or data["credits"][0]["person"]["firstName"] == "":
            director = None
        else:
            director = Actor.get_or_create_from_data(data["credits"][0]["person"])

        ret = cls(
            id=int(data["internalId"]),
            title=data["title"],
            runtime=parse_runtime(data["runtime"]),
            synopsis=data["synopsis"],
            want_to_see_count=int(data["stats"]["wantToSeeCount"]),
            poster=poster,
            director=director,
        )
        ret.save()
        ret.genres.set(Genre.get_or_create_from_data(genre) for genre in data["genres"])
        ret.cast.set(cast)
        return ret

    @classmethod
    def get_or_create_from_data(cls, data):
        """Get or create a `Movie` instance from Allocine data."""
        try:
            return cls.objects.get(id=int(data["internalId"]))
        except cls.DoesNotExist:
            ret = cls.from_allocine(data)
            ret.save()
            return ret


@dataclass
class Theater:
    """Theater dataclass."""
    id: str
    name: str
    latitude: float
    longitude: float

    @classmethod
    def get(cls, id: str) -> "Theater":
        for theater in settings.THEATERS:
            if theater.id == id:
                return theater
        raise ValueError("Theater not found")

    def get_showtimes(self, date: datetime, page: int = 1):
        """Get showtimes for a specific date."""
        showtimes: list[Showtime] = []

        datestr = date.strftime("%Y-%m-%d")
        r = requests.get(f"https://www.allocine.fr/_/showtimes/theater-{self.id}/d-{datestr}/p-{page}/")

        if r.status_code != 200:
            raise Exception(f"Error: {r.status_code} - {r.content}")

        try:
            data = r.json()
        except Exception as e:
            raise Exception(f"Can't parse JSON: {str(e)} - {r.content}")

        if data["message"] == "no.showtime.error":
            return []

        if data["message"] == "next.showtime.on":
            return []

        if data.get("error"):
            raise Exception(f"API Error: {data}")

        for result in data["results"]:
            movie = Movie.get_or_create_from_data(result["movie"])
            movie_showtimes = (
                result["showtimes"].get("dubbed", [])
                + result["showtimes"].get("original", [])
                + result["showtimes"].get("local", [])
            )

            for showtime_data in movie_showtimes:
                showtimes.append(
                    Showtime(
                        int(showtime_data["internalId"]),
                        datetime.fromisoformat(showtime_data["startsAt"]).replace(tzinfo=get_default_timezone()),
                        self.id,
                        movie=movie,
                    )
                )

        if int(data["pagination"]["page"]) < int(data["pagination"]["totalPages"]):
            showtimes.extend(self.get_showtimes(date, page + 1))

        return showtimes


class ShowtimeManager(models.Manager):
    """Custom manager for the `Showtime` model that filters out showtimes that are already passed."""
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(start_time__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        )


class Showtime(models.Model):
    """Showtime model."""
    objects = ShowtimeManager()
    all_objects = models.Manager()

    id = models.IntegerField(_("ID"), primary_key=True)
    start_time = models.DateTimeField(_("Start time"))
    theater_id = TheaterField()
    movie = models.ForeignKey("Movie", verbose_name=_("Movie"), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.movie.title} à {self.start_time.strftime('%H:%M')} à {self.theater.name}"

    class Meta:
        verbose_name = _("showtime")
        verbose_name_plural = _("showtimes")

    @property
    def theater(self) -> "Theater":
        """Get the `Theater` object corresponding to the showtime."""
        return Theater.get(self.theater_id)

    @property
    def theater_name(self):
        """Get the name of the theater corresponding to the showtime."""
        return self.theater.name
    theater_name.fget.short_description = _("Theater")
    theater_name.fget.admin_order_field = "theater_id"
