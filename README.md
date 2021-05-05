# czechm8
A simple python CLI program to download chess.com and lichess games by username(s) and build a single PGN file for later use in a Chess DB (e.g. chessx / SCID). Also, a not very funny pun.

## Usage

Setup a virtual env and download the (one) requirement
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
Run it!
```
$ ./czechm8.py magnus_lichess.pgn --lichess DrNykterstein 
Ahoj! Stáhněte si nás...
Getting lichess games for DrNykterstein... 

# Put as many usernames as you want; they'll all get downloaded
$ ./czechm8.py tacos.pgn --chess Hikaru DanielNaroditsky
...

# You can restrict downloads to only games _after_ a certain date:
$ ./czechm8.py newtacos.pgn --chess Hikaru -d 2021-03-01

```