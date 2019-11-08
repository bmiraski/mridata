"""Extract basketball game data from ESPN for input into Excel rating sheet."""

import bs4
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys


def _get_options():
    """Add options to Selenium."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return options


def getGameIdsSelenium():
    """Use Selenium to get game ids."""
    driver = webdriver.Chrome(options=_get_options())
    driver.get(SCOREBOARD)
    find_names = driver.find_elements_by_name
    box_scores = find_names('&lpos=ncb:scoreboard:boxscore')
    ids = [game.get_attribute('href')[-9:] for game in box_scores]
    print(ids, len(ids))

    driver.quit()
    return ids


def getGameIds(url):
    """Get a list of the game ids that needs to be scraped."""
    res = requests.get(url)
    games_raw = res.text
    boxscore_starts = [m.start() for m in re.finditer(
        '/mens-college-basketball/boxscore\?gameId=\d*', games_raw)]
    gamelist = []
    for game in boxscore_starts:
        id = games_raw[(game + 41):(game + 50)]
        gamelist.append(id)
    return set(gamelist)


def cleanteam(rawteam):
    """Clean the team data in ESPN to match what is in the MRI sheet."""
    teamexceptions = {"Ole Miss": "Mississippi", "Miami (OH)": "Miami (Ohio)", "NC State": "North Carolina State", "UMass": "Massachusetts", "Florida Intl": "Florida International", "Middle Tennessee": "Middle Tenn. St", "Louisiana Monroe": "Louisiana-Monroe", "UCF": "Central Florida", "Texas A&M;": "Texas A&M", "San José St": "San Jose State", "Hawai'i": "Hawaii", "California": "Cal", "Louisiana": "Louisiana-Lafayette", "UTSA": "Texas San Antonio", "Utah Valley": "Utah Valley State", "UMKC": "UM-Kansas City", "CSU Fullerton": "Cal State Fullerton", "Gardner-Webb": "Gardner Webb", "South Carolina Upstate": "USC Upstate", "Morehead St": "Morehead State", "Detroit Mercy": "Detroit", "UNC Greensboro": "UNC-Greensboro", "Fort Wayne": "Purdue Fort Wayne", "VCU": "Virginia Commonwealth", "UMass Lowell": "UMass-Lowell", "UNC Asheville": "UNC-Asheville", "McNeese": "McNeese State", "UMBC": "Md.-Baltimore Co.", "Nicholls": "Nicholls State", "Omaha": "Nebraska Omaha", "Central Connecticut": "Central Conn St.", "Jacksonville St": "Jacksonville State", "Murray St": "Murray State", "UT Martin": "Tennessee-Martin", "Milwaukee": "Wisconsin-Milwaukee", "UIC": "Illinois-Chicago", "Southern Miss": "Southern Mississippi", "Maryland-Eastern Shore": "Md.-Eastern Shore", "SE Louisiana": "Southeastern Louisiana", "Texas A&M-CC": "Texas AMCC", "Mt. St. Mary's": "Mount St. Mary's", "UL Monroe": "Louisiana-Monroe", "Florida A&M;": "Florida A&M", "UC Irvine": "UC-Irvine", "Sacramento State": "Cal State Sacramento", "Prairie View A&M": "Prairie View", "CSU Bakersfield": "Cal State Bakersfield", "CSU Northridge": "Cal State Northridge", "Tennessee St": "Tennessee State", "William & Mary": "William and Mary", "Saint Peter's": "St. Peter's", "St. Francis (BKN)": "St. Francis (NY)", "Alabama A&M;": "Alabama A&M", "North Dakota St": "North Dakota State", "UC Santa Barbara": "UCSB", "Little Rock": "Arkansas-Little Rock", "UNC Wilmington": "UNC-Wilmington", "Sam Houston State": "Sam Houston", "UT Arlington": "Texas Arlington", "Portland St": "Portland State", "Saint Mary's": "St. Mary's", "Saint Joseph's": "St. Joseph's", "North Carolina A&T;": "North Carolina A&T", "Green Bay": "Wisconsin-Green Bay", "UConn": "Connecticut", "SE Missouri St": "Southeast Missouri State", "Loyola Chicago": "Loyola-Chicago"}

    teamlist = ["Abilene Christian", "Air Force", "Akron", "Alabama", "Alabama A&M", "Alabama State", "Albany", "Alcorn State", "American", "Appalachian State", "Arizona", "Arizona State", "Arkansas", "Arkansas State", "Arkansas-Little Rock", "Arkansas-Pine Bluff", "Army", "Auburn", "Austin Peay", "Ball State", "Baylor", "Belmont", "Bethune-Cookman", "Binghamton", "Boise State", "Boston College", "Boston University", "Bowling Green", "Bradley", "Brown", "Bryant", "Bucknell", "Buffalo", "Butler", "BYU", "Cal", "Cal Poly", "Cal State Bakersfield", "Cal State Fullerton", "Cal State Northridge", "Cal State Sacramento", "California Baptist", "Campbell", "Canisius", "Central Arkansas", "Central Conn St.", "Central Florida", "Central Michigan", "Charleston", "Charleston Southern", "Charlotte", "Chattanooga", "Chicago State", "Cincinnati", "Clemson", "Cleveland State", "Coastal Carolina", "Colgate", "Colorado", "Colorado State", "Columbia", "Connecticut", "Coppin State", "Cornell", "Creighton", "Dartmouth", "Davidson", "Dayton", "Delaware", "Delaware State", "Denver", "DePaul", "Detroit", "Drake", "Drexel", "Duke", "Duquesne", "East Carolina", "East Tennessee State", "Eastern Illinois", "Eastern Kentucky", "Eastern Michigan", "Eastern Washington", "Elon", "Evansville", "Fairfield", "Fairleigh Dickinson", "Florida", "Florida A&M", "Florida Atlantic", "Florida Gulf Coast", "Florida International", "Florida State", "Fordham", "Fresno State", "Furman", "Gardner Webb", "George Mason", "George Washington", "Georgetown", "Georgia", "Georgia Southern", "Georgia State", "Georgia Tech", "Gonzaga", "Grambling", "Grand Canyon", "Hampton", "Hartford", "Harvard", "Hawaii", "High Point", "Hofstra", "Holy Cross", "Houston", "Houston Baptist", "Howard", "Idaho", "Idaho State", "Illinois", "Illinois State", "Illinois-Chicago", "Incarnate Word", "Indiana", "Indiana State", "Iona", "Iowa", "Iowa State", "IUPUI", "Jackson State", "Jacksonville", "Jacksonville State", "James Madison", "Kansas", "Kansas State", "Kennesaw State", "Kent State", "Kentucky", "La Salle", "Lafayette", "Lamar", "Lehigh", "Liberty", "Lipscomb", "Long Island University", "Long Beach State", "Longwood", "Louisiana Tech", "Louisiana-Lafayette", "Louisiana-Monroe", "Louisville", "Loyola (MD)", "Loyola Marymount", "Loyola-Chicago", "LSU", "Maine", "Manhattan", "Marist", "Marquette", "Marshall", "Maryland", "Massachusetts", "McNeese State", "Md.-Baltimore Co.", "Md.-Eastern Shore", "Memphis", "Mercer", "Merrimack", "Miami", "Miami (Ohio)", "Michigan", "Michigan State", "Middle Tenn. St", "Minnesota", "Mississippi", "Mississippi State", "Mississippi Valley State", "Missouri", "Missouri State", "Monmouth", "Montana", "Montana State", "Morehead State", "Morgan State", "Mount St. Mary's", "Murray State", "Navy", "Nebraska", "Nebraska Omaha", "Nevada", "New Hampshire", "New Mexico", "New Mexico State", "New Orleans", "Niagara", "Nicholls State", "NJIT", "Norfolk State", "North Alabama", "North Carolina", "North Carolina A&T", "North Carolina Central", "North Carolina State", "North Dakota", "North Dakota State", "North Florida", "North Texas", "Northeastern", "Northern Arizona", "Northern Colorado", "Northern Illinois", "Northern Iowa", "Northern Kentucky", "Northwestern", "Northwestern State", "Notre Dame", "Oakland", "Ohio", "Ohio State", "Oklahoma", "Oklahoma State", "Old Dominion", "Oral Roberts", "Oregon", "Oregon State", "Pacific", "Penn State", "Pennsylvania", "Pepperdine", "Pittsburgh", "Portland", "Portland State", "Prairie View", "Presbyterian", "Princeton", "Providence", "Purdue", "Purdue Fort Wayne", "Quinnipiac", "Radford", "Rhode Island", "Rice", "Richmond", "Rider", "Robert Morris", "Rutgers", "Sacred Heart", "Saint Louis", "Sam Houston", "Samford", "San Diego", "San Diego State", "San Francisco", "San Jose State", "Santa Clara", "Seattle", "Seton Hall", "SIU-Edwardsville", "Siena", "SMU", "South Alabama", "South Carolina", "South Carolina State", "South Dakota", "South Dakota State", "South Florida", "Southeast Missouri State", "Southeastern Louisiana", "Southern", "Southern Illinois", "Southern Mississippi", "Southern Utah", "St. Bonaventure", "St. Francis (NY)", "St. Francis (PA)", "St. John's", "St. Joseph's", "St. Mary's", "St. Peter's", "Stanford", "Stephen F. Austin", "Stetson", "Stony Brook", "Syracuse", "TCU", "Temple", "Tennessee", "Tennessee State", "Tennessee Tech", "Tennessee-Martin", "Texas", "Texas A&M", "Texas AMCC", "Texas Arlington", "Texas San Antonio", "Texas Southern", "Texas State", "Texas Tech", "The Citadel", "Toledo", "Towson", "Troy", "Tulane", "Tulsa", "UAB", "UC Davis", "UC Riverside", "UC-Irvine", "UCLA", "UCSB", "UM-Kansas City", "UMass-Lowell", "UNC-Asheville", "UNC-Greensboro", "UNC-Wilmington", "UNLV", "USC", "USC Upstate", "UT Rio Grande Valley", "Utah", "Utah State", "Utah Valley State", "UTEP", "Valparaiso", "Vanderbilt", "Vermont", "Villanova", "Virginia", "Virginia Commonwealth", "Virginia Tech", "VMI", "Wagner", "Wake Forest", "Washington", "Washington State", "Weber State", "West Virginia", "Western Carolina", "Western Illinois", "Western Kentucky", "Western Michigan", "Wichita State", "William and Mary", "Winthrop", "Wisconsin", "Wisconsin-Green Bay", "Wisconsin-Milwaukee", "Wofford", "Wright State", "Wyoming", "Xavier", "Yale", "Youngstown State"]
    if rawteam in teamexceptions:
        rawteama = teamexceptions[rawteam]
    else:
        rawteama = rawteam

    if rawteama not in teamlist:
        return "Not Division 1"
    else:
        return rawteama


def getteams(data):
    """Extract the teams from the matchup page data."""
    teams = data.select('.long-name')
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


def getrebsbytd(data):
    """Extract rebound dataself.

    Finds the Total Rebounds data cell and pulls the values from the next two
    data cells.
    """
    row = data.select('td')
    x = 0
    while True:
        if row[x].getText().strip() != "Rebounds":
            x += 1
        else:
            break
    rebs1 = row[x+1].getText().strip()
    rebs2 = row[x+2].getText().strip()
    return (rebs1, rebs2)


def getturnoversbytd(data):
    """Extract turnover data.

    Find the Total Turnovers data cell and pulls the data from the next two
    data cells.
    """
    row = data.select('td')
    x = 0
    while True:
        if row[x].getText().strip() != "Total Turnovers":
            x += 1
        else:
            break
    turn1 = row[x+1].getText().strip()
    turn2 = row[x+2].getText().strip()
    return (turn1, turn2)


SCOREBOARD = str(sys.argv[1])

gameIds = getGameIdsSelenium()
# gameIds = getGameIds(str(sys.argv[1]))

games = []

for game in gameIds:
    u = 'http://www.espn.com/mens-college-basketball/matchup?gameId=' + game
    games.append(u)

gamefile = open("bgamefile.txt", "w")
nond1 = 0

for x in range(0, len(games)):
    res = requests.get(games[x])
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

#    print(f"Processing {games[x]}: \n")
    gamedata = bs4.BeautifulSoup(res.text, "html.parser")
    gameteams = getteams(gamedata)
    if gameteams[0] == "Not Division 1":
        nond1 += 1
        continue
    if gameteams[1] == "Not Division 1":
        nond1 += 1
        continue
    gamescore = getscore(gamedata)
    rebounds = getrebsbytd(gamedata)
    turnovers = getturnoversbytd(gamedata)

    winner = detwinner(gamescore)

    gameoutput = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(
        gameteams[0], gameteams[1], gamescore[0], gamescore[1], rebounds[0],
        rebounds[1], turnovers[0], turnovers[1], winner[0], winner[1])

    print(gameoutput)
    gamefile.write(gameoutput)

print(f"Games skipped with Non-D1 opponents: {nond1}")
gamefile.close()
