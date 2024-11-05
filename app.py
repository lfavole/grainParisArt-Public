from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request

# IMPORT DES MODULES
from modules.Classes import Movie, Showtime, Theater

load_dotenv()

theaters: list[Theater] = []
theaters_data = json.loads(os.getenv("THEATERS", "[]"))
for theater in theaters_data:
    theaters.append(Theater(theater["id"], theater["name"], None, theater["longitude"], theater["latitude"]))


def getShowtimes(date):
    showtimes: list[Showtime] = []

    for theater in theaters:
        showtimes.extend(theater.getShowtimes(date))

    movies: list[Movie] = []

    for showtime in showtimes:
        movie = showtime.movie
        theater = showtime.theater

        if movie not in movies:
            movies.append(movie)

        movie.seances[theater.name].append(showtime.startsAt.strftime("%H:%M"))

    movies = sorted(movies, key=lambda x: x.wantToSee, reverse=True)

    return movies


showtimes = []

def load_showtimes():
    if showtimes:
        return

    for i in range(7):
        day_showtimes = getShowtimes(datetime.today() + timedelta(days=i))
        showtimes.append(day_showtimes)
        print(f"{len(day_showtimes)} séances récupéré {i+1}/7!")

app = Flask(__name__)


def translateMonth(num: int):
    return ["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"][num - 1]


def translateDay(weekday: int):
    return ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"][weekday]


@app.route("/health")
def health():
    return "OK"


@dataclass
class Day:
    index: int
    _date: datetime
    choisi: bool = False

    @property
    def jour(self):
        return translateDay(self._date.weekday())

    @property
    def chiffre(self):
        return self._date.day

    @property
    def mois(self):
        return translateMonth(self._date.month)


@app.route("/")
def home():
    delta = request.args.get("delta", default=0, type=int)

    if not (0 <= delta <= 6):
        abort(404)

    dates = []

    for i in range(7):
        dates.append(Day(i, datetime.today() + timedelta(i), i == delta))

    load_showtimes()

    return render_template(
        "index.html",
        page_actuelle="home",
        films=showtimes[delta],
        dates=dates,
        theaters=theaters,
        MAPBOX_ACCESS_TOKEN=os.getenv("MAPBOX_ACCESS_TOKEN", ""),
    )


if __name__ == "__main__":
    app.run(debug=True)
