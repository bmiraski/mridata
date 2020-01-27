"""Extract football data from ESPN for use in Excel rating sheet."""

import bs4
import re
import requests
import sys


def getGameIds(url):
    """Get a list of the game ids that needs to be scraped."""
    res = requests.get(url)
    games_raw = res.text
    boxscore_starts = [m.start() for m in re.finditer(
        'college-football/boxscore\?gameId=\d*', games_raw)]
    gamelist = []
    for game in boxscore_starts:
        id = games_raw[(game + 33):(game + 42)]
        gamelist.append(id)
    return gamelist


def cleanteam(rawteam):
    """Clean the team data from game files.

    Takes the team data from ESPN and cleans it to match what is in ratings
    spreadsheet. Also replaces non D1A teams with generic team value.
    """
    teamexceptions = {"Ole Miss": "Mississippi", "Miami (OH)": "Miami (Ohio)",
                      "NC State": "North Carolina State", "UMass":
                      "Massachusetts", "Florida Intl": "Florida International",
                      "Middle Tennessee": "Middle Tenn. St", "UL Monroe":
                      "Louisiana-Monroe", "UCF": "Central Florida",
                      "Texas A&M;": "Texas A&M", "San José State":
                      "San Jose State", "Hawai'i": "Hawaii", "California":
                      "Cal", "Louisiana": "Louisiana-Lafayette",
                      "Louisiana Monroe": "Louisiana-Monroe",
                      "UT San Antonio": "UTSA", "UConn": "Connecticut"}
    teamlist = ["Air Force", "Akron", "Alabama", "Appalachian State",
                "Arizona", "Arizona State", "Arkansas", "Arkansas State",
                "Army", "Auburn", "Ball State", "Baylor", "Boise State",
                "Boston College", "Bowling Green", "Buffalo", "BYU",
                "Cal", "Central Florida", "Central Michigan", "Charlotte",
                "Cincinnati", "Clemson", "Coastal Carolina", "Colorado",
                "Colorado State", "Connecticut", "Duke", "East Carolina",
                "Eastern Michigan", "Florida", "Florida Atlantic",
                "Florida International", "Florida State", "Fresno State",
                "Georgia", "Georgia Southern", "Georgia State",
                "Georgia Tech", "Hawaii", "Houston", "Illinois", "Indiana",
                "Iowa", "Iowa State", "Kansas", "Kansas State", "Kent State",
                "Kentucky", "Liberty", "Louisiana Tech", "Louisiana-Lafayette",
                "Louisiana-Monroe", "Louisville", "LSU", "Marshall",
                "Maryland", "Massachusetts", "Memphis", "Miami",
                "Miami (Ohio)", "Michigan", "Michigan State",
                "Middle Tenn. St", "Minnesota", "Mississippi",
                "Mississippi State", "Missouri", "Navy", "Nebraska", "Nevada",
                "New Mexico", "New Mexico State", "North Carolina",
                "North Carolina State", "North Texas", "Northern Illinois",
                "Northwestern", "Notre Dame", "Ohio", "Ohio State", "Oklahoma",
                "Oklahoma State", "Old Dominion", "Oregon", "Oregon State",
                "Penn State", "Pittsburgh", "Purdue", "Rice", "Rutgers",
                "San Diego State", "San Jose State", "SMU", "South Alabama",
                "South Carolina", "South Florida", "Southern Mississippi",
                "Stanford", "Syracuse", "TCU", "Temple", "Tennessee", "Texas",
                "Texas A&M", "Texas State", "Texas Tech", "Toledo", "Troy",
                "Tulane", "Tulsa", "UAB", "UCLA", "UNLV", "USC", "Utah State",
                "Utah", "UTEP", "UTSA", "Vanderbilt", "Virginia",
                "Virginia Tech", "Wake Forest", "Washington",
                "Washington State", "West Virginia", "Western Kentucky",
                "Western Michigan", "Wisconsin", "Wyoming"]
    if rawteam in teamexceptions:
        rawteama = teamexceptions[rawteam]
    else:
        rawteama = rawteam

    if rawteama not in teamlist:
        return "Non D1A"
    else:
        return rawteama


def getteams(data):
    """Extract the teams from the matchup page data."""
    teams = data.select('.long-name')
    if len(teams) == 0:
        return "error_game"
    team1 = cleanteam(teams[0].getText())
    team2 = cleanteam(teams[1].getText())
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
    return "error_game"


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


gameIds = getGameIds(str(sys.argv[1]))

games = []

for game in gameIds:
    u = 'http://www.espn.com/college-football/matchup?gameId=' + game
    games.append(u)

print(games)
print(len(games))

gamefile = open("gamefile.txt", "w")
error_games = []

for x in range(0, len(games)):
    res = requests.get(games[x])
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    gamedata = bs4.BeautifulSoup(res.text, "html.parser")
    gameteams = getteams(gamedata)
    if gameteams == "error_game":
        error_games.append(games[x])
        continue
    gamescore = getscore(gamedata)
    rushyards = getrush(gamedata)
    if rushyards == "error_game":
        error_games.append(games[x])
        continue
    passyards = getpass(gamedata)
    turnovers = getturnovers(gamedata)

    winner = detwinner(gamescore)

    gameoutput = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(
        gameteams[0], gameteams[1], gamescore[0], gamescore[1],
        rushyards[0], rushyards[1], passyards[0], passyards[1],
        turnovers[0], turnovers[1], winner[0], winner[1])

    print(gameoutput)
    gamefile.write(gameoutput)

if len(error_games) > 0:
    print(f"The following games were not processed due to an error: {error_games}")
gamefile.close()
