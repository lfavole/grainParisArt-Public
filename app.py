from dataclasses import dataclass
from datetime import datetime, timedelta

from flask import Flask, abort, render_template, request

# IMPORT DES MODULES
from modules.Classes import Movie, Showtime, Theater

theaters = [
    Theater("C0071", "Écoles Cinéma Club", None, 2.348973, 48.848363),
    Theater("C2954", "MK2 Bibliothèque", None, 2.375488, 48.832448),
    Theater("C0050", "MK2 Beaubourg", None, 2.352312, 48.861584),
    Theater("W7504", "Épée de bois", None, 2.349555, 48.841300),
    Theater("C0076", "Cinéma du Panthéon", None, 2.342385, 48.847488),
    Theater("C0089", "Max Linder Panorama", None, 2.344856, 48.871370),
    Theater("C0013", "Luminor Hotel de Ville", None, 2.353602, 48.858676),
    Theater("C0072", "Le Grand Action", None, 2.352129, 48.847530),
    Theater("C0099", "MK2 Parnasse", None, 2.330526, 48.842813),
    Theater("C0073", "Le Champo", None, 2.343223, 48.849980),
    Theater("C0020", "Filmothèque du Quartier Latin", None, 2.342790, 48.849510),
    Theater("C0074", "Reflet Medicis", None, 2.342790, 48.849510),
    Theater("C0159", "UGC Ciné Cité Les Halles", None, 2.343014, 48.849777),
    Theater("C0026", "UGC Ciné Cité Bercy", None, 2.546596, 48.840113),
]


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

    return render_template("index.html", page_actuelle="home", films=showtimes[delta], dates=dates, theaters=theaters)


if __name__ == "__main__":
    app.run(debug=True)
