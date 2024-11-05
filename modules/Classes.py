from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import requests


class Movie:
    def __init__(self, data) -> None:
        self.data = data
        self.title = data["title"]
        self.id = data["internalId"]
        self.runtime = data["runtime"]
        self.synopsis = data["synopsis"]
        self.genres = [genre["translate"] for genre in data["genres"]]
        self.wantToSee = data["stats"]["wantToSeeCount"]
        try:
            self.affiche = data["poster"]["url"]
        except (TypeError, KeyError):
            self.affiche = "/static/images/nocontent.png"

        self.cast = []

        # Noms des acteurs
        for actor in data["cast"]["edges"]:
            if actor["node"]["actor"] is None:
                continue

            name = f'{actor["node"]["actor"].get("firstName", "")} {actor["node"]["actor"].get("lastName", "")}'
            name = name.lstrip()
            self.cast.append(name)

        # Nom du réalisateur
        if len(data["credits"]) == 0:
            self.director = "Inconnu"
        else:
            self.director = f'{data["credits"][0]["person"].get("firstName", "")} {data["credits"][0]["person"].get("lastName", "")}'
            self.director = self.director.lstrip()

        self.seances: defaultdict[str, list[str]] = defaultdict(list)

    def __hash__(self):
        return hash(self.title)

    def __eq__(self, other):
        return self.title == other.title

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.title}>"

    @property
    def url(self):
        return f"https://www.allocine.fr/film/fichefilm_gen_cfilm={self.id}.html"


class Showtime:
    def __init__(self, data, theather, movie: Movie) -> None:
        self.startsAt = datetime.fromisoformat(data["startsAt"])
        self.diffusionVersion = data["diffusionVersion"]
        self.services = data["service"]
        self.theater: Theater = theather
        self.movie = movie

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.movie.title} startsAt={self.startsAt}>"


@dataclass
class Theater:
    id: str
    name: str
    location: dict | None
    longitude: float
    latitude: float

    def getShowtimes(
        self, date: datetime, page: int = 1, showtimes: list = None, movies: dict[str, Movie] = None
    ) -> list[Showtime]:
        if showtimes is None:
            showtimes = []
        if movies is None:
            movies = {}

        datestr = date.strftime("%Y-%m-%d")
        r = requests.get(f"https://www.allocine.fr/_/showtimes/theater-{self.id}/d-{datestr}/p-{page}/")
        r.raise_for_status()

        data = r.json()

        if data["message"] == "no.showtime.error":
            return []

        if data["message"] == "next.showtime.on":
            return []

        if data.get("error"):
            raise Exception(f"API Error: {data}")

        for movie in data["results"]:
            inst = movies.setdefault(movie["movie"]["title"], Movie(movie["movie"]))
            movie_showtimes = (
                movie["showtimes"].get("dubbed", [])
                + movie["showtimes"].get("original", [])
                + movie["showtimes"].get("local", [])
            )

            for showtime_data in movie_showtimes:
                showtimes.append(Showtime(showtime_data, self, inst))

        if int(data["pagination"]["page"]) < int(data["pagination"]["totalPages"]):
            return self.getShowtimes(date, page + 1, showtimes, movies)

        return showtimes

    @staticmethod
    def new(query: str):
        r = requests.get(f"https://www.allocine.fr/_/localization_city/{query}")

        data = r.json()

        if len(data["values"]["theaters"]) == 0:
            raise Exception("Not found")

        theater = data["values"]["theaters"][0]["node"]
        return Theater(theater["name"], theater["internalId"], theater["location"])


if __name__ == "__main__":
    cgr = Theater.new("CGR Brest Le Celtic")
    print(f"{cgr.name} ({cgr.id})")
    print(f"{cgr.location['zip']} {cgr.location['city']}")

    showtimes = cgr.getShowtimes(datetime.today())

    print(showtimes[0])
