import requests
import bs4

def cleanteam(rawteam):
    """Cleans the team data in ESPN to match what is in the MRI sheet"""
    teamexceptions = {"Ole Miss": "Mississippi", "Miami (OH)": "Miami (Ohio)", "NC State": "North Carolina State",
                      "UMass": "Massachusetts", "Florida Intl": "Florida International", "Middle Tennessee":
                          "Middle Tenn. St", "Louisiana Monroe": "Louisiana-Monroe", "UCF": "Central Florida",
                      "Texas A&M;": "Texas A&M", "San José State": "San Jose State", "Hawai'i": "Hawaii", "California":
                      "Cal", "Louisiana": "Louisiana-Lafayette", "UT San Antonio": "UTSA"}
    if rawteam in teamexceptions:
        return teamexceptions[rawteam]
    else:
        return rawteam

def getteams(data):
    """Extracts the teams from the matchup page data"""
    teams = data.select('.long-name')
    team1 = cleanteam(teams[0].getText())
    team2 = cleanteam(teams[1].getText())
    return (team1, team2)

def getscore(data):
    """ Determines the game score from the set of game data"""
    scores = data.select('.score')
    score1 = scores[0].getText()
    score2 = scores[1].getText()
    return (score1, score2)

def detwinner(score):
    """ Uses the game score to determine the winner"""
    scoreteam1 = int(score[0])
    scoreteam2 = int(score[1])
    if scoreteam1 > scoreteam2:
        return (1,0)
    else:
        return (0,1)

def getrebs(data):
    """ Extracts the team rebound data from the data set. For some reason this returns a four item list so select
    items 0 and 2 for the actual data."""
    rebs = data.select("tr.highlight td.reb")

    rebs1 = rebs[0].getText().strip()
    rebs2 = rebs[2].getText().strip()
    return (rebs1, rebs2)

def getturnovers(data):
    """ Extracts the passing data from the game data by finding the td tag that contains 'passing'
    and selecting the text from the next two td tags. Text must be trimmed because of formatting
    on the page."""
    turns = data.select("tr.highlight td.to")

    turn1 = turns[0].getText().strip()
    turn2 = turns[2].getText().strip()
    return (turn1, turn2)

g = open("C:\\Users\\MILES_DAVIS\\Desktop\\stats\\bgamelist.txt", "r")

games = g.readlines()
for x in range(0,len(games)-1):
    a = games[x]
    newx = a[0:len(a)-1]
    games[x] = newx
print(games)
g.close()

#gamefile = open("C:\\Users\\MILES_DAVIS\\Desktop\\stats\\gamefile.txt", "w")

for x in range(0,len(games)):
    res=requests.get(games[x])
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    gamedata = bs4.BeautifulSoup(res.text, "html.parser")
    gameteams = getteams(gamedata)
    gamescore = getscore(gamedata)
    rebounds = getrebs(gamedata)
    turnovers = getturnovers(gamedata)

    winner = detwinner(gamescore)

    gameoutput = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(gameteams[0], gameteams[1],
                                                                                   gamescore[0], gamescore[1],
                                                             rebounds[0], rebounds[1], turnovers[0], turnovers[1],
                                                             winner[0], winner[1])

    print(gameoutput)
#    gamefile.write(gameoutput)

#gamefile.close()