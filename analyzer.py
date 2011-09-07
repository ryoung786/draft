#! /usr/bin/python

from BeautifulSoup import BeautifulSoup
import urllib2

values_url = 'http://sports.espn.go.com/fantasy/football/ffl/story?page=NFLDK2K11ranks'

players = []
values  = []
for suffix in ['QB', 'RB', 'WR', 'TE', 'DST', 'K']:
    resp = urllib2.urlopen(values_url + suffix)
    html = resp.read()
    dom = BeautifulSoup(html)
    rows = dom.findAll("tr", { "class" : "last" })

    players += [row.td.nextSibling.a.string.strip() for row in rows]
    values  += [row.td.nextSibling.nextSibling.nextSibling.string.strip() for row in rows]
    

# OK, now we've got parallel lists.  Let's make that a more manageable
# hash lookup
pre_draft_valuations = {}
for player, value in zip(players, values):
    pre_draft_valuations[player] = value





