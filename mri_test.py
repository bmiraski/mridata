import pandas as pd

from collections import defaultdict
from teamData import basketballTeamList as teamlist


def determineRecord(df):
    """Determine record for each team by reading from dataframe."""
    team_record = defaultdict()
    for team in teamlist:
        expr1 = 'Team1 == "' + team + '"'
        expr2 = 'Team2 == "' + team + '"'
        wins = df.query(expr1)['WT1'].sum() + df.query(
            expr2)['WT2'].sum()
        losses = df.query(expr1)['WT2'].sum() + df.query(
            expr2)['WT1'].sum()
        team_record[team] = (wins, losses)
    return team_record


def determineOpponentsRecord(df):
    """Determine Opponents Record for each team."""
    opp_record = defaultdict()
    for team in teamlist:
        expr1 = 'Team1 == "' + team + '"'
        expr2 = 'Team2 == "' + team + '"'
        wins = df.query(expr1)['T2W'].sum() + df.query(
            expr2)['T1W'].sum()
        losses = df.query(expr1)['T2L'].sum() + df.query(
            expr2)['T1L'].sum()
        opp_record[team] = (wins, losses)
    return opp_record


def determineTeamOnePoints(df):
    """Determine the weight MOV array for Team One."""
    t1points = []
    for x in range(0, df.Team1.count()):
        score_diff = df.Pnt1.ix[x] - df.Pnt2.ix[x]
        opp_win_perc = (df.T2W.ix[x] / (df.T2W.ix[x] + df.T2L.ix[x]))
        opp_lose_perc = (df.T2L.ix[x] / (df.T2W.ix[x] + df.T2L.ix[x]))
        otwo_win_perc = (df.T2OW.ix[x] / (df.T2OW.ix[x] + df.T2OL.ix[x]))
        otwo_lose_perc = (df.T2OL.ix[x] / (df.T2OW.ix[x] + df.T2OL.ix[x]))
        if df.WT1.ix[x] == 1:
            if score_diff > 30:
                score_diff = 30
            points = score_diff * opp_win_perc * otwo_win_perc
        else:
            if score_diff < -30:
                score_diff = -30
            points = score_diff * opp_lose_perc * otwo_lose_perc
        t1points.append(points)
    return t1points


def determineTeamTwoPoints(df):
    """Determine the weight MOV array for Team Two."""
    t2points = []
    for x in range(0, df.Team2.count()):
        score_diff = df.Pnt2.ix[x] - df.Pnt1.ix[x]
        opp_win_perc = (df.T1W.ix[x] / (df.T1W.ix[x] + df.T1L.ix[x]))
        opp_lose_perc = (df.T1L.ix[x] / (df.T1W.ix[x] + df.T1L.ix[x]))
        otwo_win_perc = (df.T1OW.ix[x] / (df.T1OW.ix[x] + df.T1OL.ix[x]))
        otwo_lose_perc = (df.T1OL.ix[x] / (df.T1OW.ix[x] + df.T1OL.ix[x]))
        if df.WT2.ix[x] == 1:
            if score_diff > 30:
                score_diff = 30
            points = score_diff * opp_win_perc * otwo_win_perc
        else:
            if score_diff < -30:
                score_diff = -30
            points = score_diff * opp_lose_perc * otwo_lose_perc
        t2points.append(points)
    return t2points


def addRecords(df):
    """Add columns for team records to the main dataframe."""
    team_record = determineRecord(df)
    teamOneWins = [team_record[row][0] for row in df.Team1]
    teamOneLosses = [team_record[row][1] for row in df.Team1]
    teamTwoWins = [team_record[row][0] for row in df.Team2]
    teamTwoLosses = [team_record[row][1] for row in df.Team2]
    df_records = pd.DataFrame({'T1W': teamOneWins,
                               'T1L': teamOneLosses,
                               'T2W': teamTwoWins,
                               'T2L': teamTwoLosses})

    df = pd.concat([df, df_records], axis=1)
    return df


def addOpponentsRecords(df):
    """Add columns for opponent records to the main dataframe."""
    opp_record = determineOpponentsRecord(df)
    teamOneOpponentWins = [opp_record[row][0] for row in df.Team1]
    teamOneOpponentLosses = [opp_record[row][1] for row in df.Team1]
    teamTwoOpponentWins = [opp_record[row][0] for row in df.Team2]
    teamTwoOpponentLosses = [opp_record[row][1] for row in df.Team2]
    df_opp_records = pd.DataFrame({'T1OW': teamOneOpponentWins,
                                   'T1OL': teamOneOpponentLosses,
                                   'T2OW': teamTwoOpponentWins,
                                   'T2OL': teamTwoOpponentLosses})

    df = pd.concat([df, df_opp_records], axis=1)
    return df


df = pd.read_csv('basketgamedata.csv')

print(df.head())

# df_sum1 = df.groupby('Team1')
# print(df_sum1.sum().head())

# df_sum2 = df.groupby('Team2')
# print(df_sum2.sum().head())

df = addRecords(df)
df = addOpponentsRecords(df)

df['T1Point'] = determineTeamOnePoints(df)
df['T2Point'] = determineTeamTwoPoints(df)

print(df.head())
print(df.tail())
