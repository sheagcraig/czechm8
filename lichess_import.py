import argparse
import datetime
import os
import pathlib
import re
import time

import requests


LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN", "")


def main():
    args = parse_args()
    if not LICHESS_TOKEN:
        exit("No LICHESS_TOKEN to upload with!")
    # pgn = pathlib.Path(args.pgn).expanduser().read_text()
    if args.date:
        from_date = datetime.date.fromisoformat(args.date)
    else:
        from_date = datetime.date.fromtimestamp(0)
    raw_games = get_chess_games(args.chess_user, from_date)
    games = split_games(raw_games)

    post_games(games)


def parse_args():
    parser = argparse.ArgumentParser(description="Import games from a bulk PGN to Lichess")
    parser.add_argument('chess_user', help="Chess.com username from which to pull games")
    parser.add_argument(
        "-d",
        "--date",
        help="ISO8601 date (YYYY-MM-DD) after which games will be downloaded. Defaults to 1969-12-31",
    )
    return parser.parse_args()


def get_chess_games(user, from_date):
    games = []
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
        # if url_date.year == from_date.year and url_date.month == from_date.month:
        #     pgn = date_filter_games(pgn, from_date)
        games.append(pgn)
        # The monthly archive omits months with no games, so there's
        # always at least one. The triple newline will only be present
        # if there is a second game, so a classic off by one situation.
        count = pgn.count("\n\n\n") + 1
        print(f"{url} {count} games ✅")

    return "\n\n".join(games)


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


def split_games(raw_games):
    games = []
    pattern = re.compile(r'.*(1\-?0|0\-?1|1/2\-?1/2|\*)$')
    lines = raw_games.splitlines()
    game = []
    for line in lines:
        game.append(line)

        if pattern.match(line):
            games.append(game)
            game = []
    return ["\n".join(g) for g in games]


def post_games(games):
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {LICHESS_TOKEN}'})

    for game in games:
        response = None
        while not response or response.status_code != requests.codes.OK:
            breakpoint()
            response = session.post('https://lichess.org/api/import', json={'pgn': game})
            print(response.text)
            if response.status_code != requests.codes.OK:
                time.sleep(61)


if __name__ == "__main__":
    main()