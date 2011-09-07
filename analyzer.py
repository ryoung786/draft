#! /usr/bin/python
from BeautifulSoup import BeautifulSoup
from operator import itemgetter
import urllib2, sys

league     = sys.argv[1]
values_url = 'http://sports.espn.go.com/fantasy/football/ffl/story?page=NFLDK2K11ranks'
recap_url  = 'http://games.espn.go.com/ffl/tools/draftrecap?leagueId=' + league

# Handle the http request and return a searchable html object
def curl(url):
    resp = urllib2.urlopen(url)
    html = resp.read()
    return BeautifulSoup(html)

# Selects the appropriate cell, rips out the position and
# standardizes the return string (stripped and lowercased)
# row: BeautifulSoup element
def grabPlayerName(row):
    cell = row.td.nextSibling
    name = cell.a.string.strip()

    # TODO: bug here -- D/ST is repeated twice, so all D's are $0
    team = cell.contents[-1].string.strip()

    # this is nasty, but the ESPN site dumps in this garbage in their markup,
    # so let's get rid of it, since this is our lookup key
    if '&nbsp;' in team:
        team = team[0 : team.find('&nbsp;')]
    return "{0} {1}".format(name, team).lower()

# Selects the appropriate cell, then strips the $ sign and returns an int
# row: BeautifulSoup element, a tr
# recap: True if this is a row from the Draft Recap table, False otherwise
def grabCashValue(row, recap=False):
    if recap:
        cash = row.td.nextSibling.nextSibling.string.strip()
        return int(cash[1:])
    else:
        cash = row.td.nextSibling.nextSibling.nextSibling.string.strip()
        return int(cash[1:])

players = []
values  = []
for suffix in ['QB', 'RB', 'WR', 'TE', 'DST', 'K']:
    dom = curl(values_url + suffix)
    rows = dom.findAll("tr", { "class" : "last" })

    players += [grabPlayerName(row) for row in rows]
    values  += [grabCashValue(row) for row in rows]

# OK, now we've got parallel lists.  Let's make that a more
# manageable dict
pre_draft_valuations = {}
for player, value in zip(players, values):
    pre_draft_valuations[player] = value


# Time to get the draft recap
dom = curl(recap_url)

container = dom.find('div', {'class':'games-fullcol games-fullcol-extramargin'})
teams_dom = container.table.findAll('table')

# Now we've got all our teams.  We've got to group them up now
# into a dict we can query and analyze easily

total_teams = len(teams_dom)
teams = {} # maps team name -> [(player, valuation, paid, diff)]
for team in teams_dom:
    name = team.tr.td.a.string.strip()
    team_data = []
    for row in team.findAll('tr', {'class' : 'tableBody'}):
        player = grabPlayerName(row)
        cash   = grabCashValue(row, recap=True)
        # scale the valuation, because the site numbers are for a 10-team league
        valuation = pre_draft_valuations.get(player, 0) * (total_teams / 10.0)
        team_data += [( player, valuation, cash, cash - valuation )]

    teams[name] = team_data

# Cool, we've got all our data.  Now let's use it to display
# which team did the best value-wise
foo = []
for team, data in teams.items():
    foo += [ (team, sum( [x[3] for x in data] )) ]

foo = sorted(foo, key=itemgetter(1))
for name, value in foo:
    print '{0}: {1:.2f}'.format(name, value)
