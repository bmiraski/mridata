"""Extract football data from ESPN for use in Excel rating sheet."""

import bs4
import re
import requests
import sys
import datetime


def generateScoreboardList():
    """Generate a list of scoreboard URLs for scraping."""
    urls = []
    yr = 2019
    while yr < 2019:
        for week in range(1, 18):
            url = f"https://www.espn.com/nfl/scoreboard/_/year/{yr}/seasontype/2/week/{week}"
            urls.append(url)
        yr += 1
    for week in range(1, 5):
        url = f"https://www.espn.com/nfl/scoreboard/_/year/{yr}/seasontype/2/week/{week}"
        urls.append(url)
    return urls


def getGameIds(url):
    """Get a list of the game ids that needs to be scraped."""
    res = requests.get(url)
    games_raw = res.text
    boxscore_starts = [m.start() for m in re.finditer(
        'nfl/boxscore\?gameId=\d*', games_raw)]
    gamelist = []
    for game in boxscore_starts:
        id = games_raw[(game + 20):(game + 29)]
        gamelist.append(id)

    games = []
    for game in gamelist:
        u = 'http://www.espn.com/nfl/matchup?gameId=' + game
        games.append(u)
    return games


def getteams(data):
    """Extract the teams from the matchup page data."""
    teams = data.select('.abbrev')
    team1 = teams[0].getText()
    team2 = teams[1].getText()
    return (team1, team2)


def getscore(data):
    """Determine the game score from the set of game data."""
    scores = data.select('.score')
    score1 = scores[0].getText()
    score2 = scores[1].getText()
    return (score1, score2)


def detwinner(score):
    """Use the game score to determine the winner."""
    scoreteam1 = int(score[0])
    scoreteam2 = int(score[1])
    if scoreteam1 > scoreteam2:
        return (1, 0)
    else:
        return (0, 1)


def getrush(data):
    """Extract the rushing data from the game data.

    Finds the td tag that contains 'Rushing' and selects the text from the next
    two td tags. Text must be trimmed because of formatting on the page.
    """
    row = data.select('td')
    x = 0
    while x < len(row):
        if row[x].getText().strip() != "Rushing":
            x += 1
        else:
            rush1 = row[x+1].getText().strip()
            rush2 = row[x+2].getText().strip()
            return (rush1, rush2)
    return "Error"


def getpass(data):
    """Extract the passing data from the game data.

    Finds the td tag that contains 'Passing' and selects the text from the next
    two td tags. Text must be trimmed because of formatting on the page.
    """
    row = data.select('td')
    x = 0
    while True:
        if row[x].getText().strip() != "Passing":
            x += 1
        else:
            break
    pass1 = row[x+1].getText().strip()
    pass2 = row[x+2].getText().strip()
    return (pass1, pass2)


def getturnovers(data):
    """Extract the turnover data from the game data.

    Finds the td tag that contains 'Turnovers' and selects the text from the
    next two td tags. Text must be trimmed because of formatting on the page.
    """
    row = data.select('td')
    x = 0
    while True:
        if row[x].getText().strip() != "Turnovers":
            x += 1
        else:
            break
    turn1 = row[x + 1].getText().strip()
    turn2 = row[x + 2].getText().strip()
    return (turn1, turn2)


def getmeta(data):
    """Pull game metadata (date, line, o/u)."""
    datedata = data.select('span[data-date]')[0]
    datelist = [m.start() for m in re.finditer('\d*-\d*-\d*T\d*:\d*Z',
                                               str(datedata))]
    datestart = datelist[0]
    date = str(datedata)[datestart: (datestart + 17)]
    date = adjustdate(date)

    ouli = data.select('.ou')
    if len(ouli) > 0:
        ou = ouli[0].getText().strip()[-2:]
    else:
        ou = ""

    lis = data.select("li")
    # print(lis)
    for li in lis:
        if li.getText()[0:5] == "Line:":
            line = li.getText()[6:]
            break
        else:
            line = ""

    stad = data.select('.caption-wrapper')
    if len(stad) > 0:
        stadium = stad[0].getText().strip()
    else:
        stadium = ""

    return (date[0], date[1], line, ou, stadium)


def adjustdate(date):
    """Convert date string into date and timing of game."""
    startyear = int(date[0:4])
    startmonth = int(date[5:7])
    startday = int(date[8:10])
    hour = int(date[11:13])
    rawdate = datetime.datetime(startyear, startmonth, startday, hour)
    newdate = rawdate - datetime.timedelta(hours=5)
    datestring = f"{str(newdate.month)}/{str(newdate.day)}/{str(newdate.year)}"
    if hour - 5 in range(1, 14):
        gametime = "E"
    elif hour - 5 in range(14, 18):
        gametime = "L"
    else:
        gametime = "N"
    return (datestring, gametime)


def pullGameData(game, season, wk):
    res = requests.get(game)
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))
        error_games.append(game)
        return "Error"

    gamedata = bs4.BeautifulSoup(res.text, "html.parser")
    gameteams = getteams(gamedata)
    gamescore = getscore(gamedata)
    rushyards = getrush(gamedata)
    if rushyards == "Error":
        error_games.append(game)
        return "Error"

    passyards = getpass(gamedata)
    turnovers = getturnovers(gamedata)
    gamemeta = getmeta(gamedata)

    winner = detwinner(gamescore)

    gameoutput = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18}\n".format(
        season, wk, gamemeta[0], gamemeta[1], gamemeta[2], gamemeta[3], gamemeta[4],
        gameteams[0], gameteams[1], gamescore[0], gamescore[1], rushyards[0],
        rushyards[1], passyards[0], passyards[1], turnovers[0], turnovers[1],
        winner[0], winner[1])

    return gameoutput


def processWeek(season, wk):
    scoreboard_url = f"https://www.espn.com/nfl/scoreboard/_/year/{season}/seasontype/2/week/{wk}"

    games = getGameIds(scoreboard_url)

    for game in games:
        game_output = pullGameData(game, season, wk)
        if game_output == "Error":
            continue
        else:
            print(game_output)
            gamefile.write(game_output)


# scoreboards = generateScoreboardList()
# scoreboards = ['https://www.espn.com/nfl/scoreboard/_/year/2019/seasontype/2/week/3']

gamefile = open("gamefilenfl.txt", "w")
error_games = []

seasons = list(range(2019, 2020))
for season in seasons:
    if season != 2019:
        for wk in range(1, 18):
            processWeek(season, wk)
    else:
        for wk in range(1, 18):
            processWeek(season, wk)

print(error_games)
gamefile.close()
