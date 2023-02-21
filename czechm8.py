#!/usr/bin/env python3
"""
Download a user's lichess and chess.com games into a single PGN.

Adapted from:
https://www.reddit.com/r/chess/comments/9ifkaq/how_i_downloaded_all_my_chesscom_games_using/

[chess.com API](https://www.chess.com/news/view/published-data-api)
[lichess API]()
"""


import argparse
import datetime
import json
import pathlib
import re
import time

import requests


def get_args():
    parser = argparse.ArgumentParser(
        description="Download lichess and chess.com games into a single PGN"
    )
    parser.add_argument("filename", help="Output filename")
    parser.add_argument(
        "-l",
        "--lichess",
        help="lichess account names to retrieve",
        action="append",
        type=str,
        default=[],
    )
    parser.add_argument(
        "-c",
        "--chess",
        help="chess.com account names to retrieve",
        action="append",
        type=str,
        default=[],
    )
    parser.add_argument(
        "-d",
        "--date",
        help="ISO8601 date (YYYY-MM-DD) after which games will be downloaded. Defaults to 1969-12-31",
    )

    return parser.parse_args()


def get_lichess_games(users, from_date):
    # https://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python
    # Note, this doesn't handle TZ offset!
    dtt = from_date.timetuple()
    timestamp = int(time.mktime(dtt))
    games = []
    for user in users:
        print(f"Getting lichess games for {user}...")
        url = f"https://lichess.org/api/games/user/{user}"
        response = requests.get(url, params={"since": timestamp})
        count = response.text.count("\n\n\n")
        print(f"{url} {count} games ✅")
        games.append(response.text)

    return games


def get_chess_games(users, from_date):
    games = []
    for user in users:
        print(f"Getting chess.com games for {user}...")
        url = f"https://api.chess.com/pub/player/{user}/games/archives"
        try:
            response = requests.get(url).json()
        except:
            response = {}
        monthly_archives = response.get("archives", [])

        for url in monthly_archives:
            segments = url.split("/")
            year, month = segments[-2:]
            url_date = datetime.date(year=int(year), month=int(month), day=1)
            if url_date < from_date and not (
                url_date.year == from_date.year and url_date.month == from_date.month
            ):
                continue
            response = requests.get(f"{url}/pgn")
            pgn = response.text
            if url_date.year == from_date.year and url_date.month == from_date.month:
                pgn = date_filter_games(pgn, from_date)
            games.append(pgn)
            # The monthly archive omits months with no games, so there's
            # always at least one. The triple newline will only be present
            # if there is a second game, so a classic off by one situation.
            count = pgn.count("\n\n\n") + 1
            print(f"{url} {count} games ✅")

    return games


def date_filter_games(pgn, from_date):
    filtered = []
    for game in pgn.split("\n\n\n"):
        found = re.search(
            r'\[UTCDate "(?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2})', game
        )
        if found:
            bits = found.groupdict()
            match_date = datetime.date(
                year=int(bits["year"]), month=int(bits["month"]), day=int(bits["day"])
            )
            if match_date < from_date:
                continue
        filtered.append(game)

    return "".join(filtered)


def write_pgn(filename, games):
    pathlib.Path(filename).write_text("".join(games))


def main():
    args = get_args()
    games = []
    if args.date:
        from_date = datetime.date.fromisoformat(args.date)
    else:
        from_date = datetime.date.fromtimestamp(0)
    print("Ahoj! Stáhněte si nás...")
    games.extend(get_lichess_games(args.lichess, from_date))
    games.extend(get_chess_games(args.chess, from_date))
    write_pgn(args.filename, games)
    print("Všechny práce byly dokončeny!")


if __name__ == "__main__":
    main()
