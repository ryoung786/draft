#! /usr/bin/python

from BeautifulSoup import BeautifulSoup
import urllib2

values_url = 'http://sports.espn.go.com/fantasy/football/ffl/story?page=NFLDK2K11ranks'
recap_url = 'http://games.espn.go.com/ffl/tools/draftrecap?leagueId=604965'

def curl(url):
    resp = urllib2.urlopen(url)
    html = resp.read()
    return BeautifulSoup(html)

players = []
values  = []
for suffix in ['QB', 'RB', 'WR', 'TE', 'DST', 'K']:
    dom = curl(values_url + suffix)
    rows = dom.findAll("tr", { "class" : "last" })

    players += [row.td.nextSibling.a.string.strip() for row in rows]
    values  += [row.td.nextSibling.nextSibling.nextSibling.string.strip() for row in rows]

# get rid of the leading $
values = [int(x[1:]) for x in values]


# OK, now we've got parallel lists.  Let's make that a more
# manageable dict
pre_draft_valuations = {}
for player, value in zip(players, values):
    pre_draft_valuations[player] = value


# Time to get the draft recap
dom = curl(recap_url)

container = dom.find('div', {'class' : 'games-fullcol games-fullcol-extramargin'})
teams_dom = container.table.findAll('table')

# Now we've got all our teams.  We've got to group them up now
# into a dict we can query and analyze easily

teams = {} # maps team name -> [ { player: player_name, valuation: $, paid: $ } ]

for team in teams_dom:
    name = team.tr.td.a.string.strip()
    team_data = []
    for row in team.findAll('tr', {'class' : 'tableBody'}):
        player = row.td.nextSibling.a.string.strip()
        cash   = row.td.nextSibling.nextSibling.string.strip()
        team_data += [{ 'player': player,
                        'valuation' : pre_draft_valuations.get(player, '$0'),
                        'paid' : int(cash[1:]) }]
    teams[name] = team_data

spent = sum([ data['paid'] for data in teams['FREE WEEZY']])

