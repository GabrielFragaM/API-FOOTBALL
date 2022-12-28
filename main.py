import http.client
import csv

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
}


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def get_team_details(team_id, teams):
    if teams['home']['id'] == team_id:
        return {
            'id': team_id,
            'name': teams['home']['name'],
            'play_home': 'yes',
            'play': 'home',
            'winner': teams['home']['winner']
        }
    else:
        return {
            'id': team_id,
            'name': teams['away']['name'],
            'play_home': 'no',
            'play': 'away',
            'winner': teams['away']['winner']
        }


def get_adversary_details(team_id, teams):
    if teams['home']['id'] != team_id:
        return {
            'id': teams['home']['id'],
            'name': teams['home']['name'],
            'play': 'home',
        }
    else:
        return {
            'id': teams['away']['id'],
            'name': teams['away']['name'],
            'play': 'away',
        }


def get_events(fixture, team):
    query_params = '?' + fixture + '&' + team

    conn.request("GET", "/fixtures/events" + query_params, headers=headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")


def get_lineups(fixture, team):
    query_params = '?' + fixture + '&' + team

    conn.request("GET", "/fixtures/lineups" + query_params, headers=headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")


def get_statistics(fixture, team):
    query_params = '?' + fixture + '&' + team

    conn.request("GET", "/fixtures/statistics" + query_params, headers=headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")


def get_fixtures(league, season, team, status):
    query_params = '?' + league + \
                   '&' + season + \
                   '&' + team + \
                   '&' + status

    conn.request("GET", "/fixtures" + query_params, headers=headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")


def define_csv_final(fixture, statistics, events, lineups, team):
    def define_statistics():
        statistics_final = {}

        for info in statistics['statistics']:
            statistics_final[info['type']] = info['value']

        return statistics_final

    def define_events():
        events_final = {}

        for info in events:
            if info['team']['id'] == team:
                events_final['team_event_main'] = info['type']
                events_final['team_event_detail'] = info['detail']
                events_final['team_event_player'] = info['player']['name']
                events_final['team_event_time'] = info['time']['elapsed']
                events_final['team_event_assist'] = info['assist']['name']
            else:
                events_final['adversary_event_main'] = info['type']
                events_final['adversary_event_detail'] = info['detail']
                events_final['adversary_event_player'] = info['player']['name']
                events_final['adversary_event_time'] = info['time']['elapsed']
                events_final['adversary_event_assist'] = info['assist']['name']

        return events_final

    def define_lineups():
        def get_players(team_info, start_players, substitutes_players):
            players_map = {}
            substitutes_map = {}

            for substitute in substitutes_players:
                substitutes_map[team_info + 'substitute_pos' + substitute['player']['pos'] + 'substitute_grid_' +
                                substitute['player']['grid']] = substitute['player']['name']

            for player in start_players:
                players_map[team_info + 'player_pos' + player['player']['pos'] + 'player_grid_' +
                            player['player']['grid']] = player['player']['name']

            return merge_dicts(players_map, substitutes_map)

        lineups_final = {}

        if lineups[0]['team']['id'] == team:
            lineups_final['team_formation'] = lineups[0]['formation']
            lineups_final['coach'] = lineups[0]['coach']['name']
            players = get_players('team_', lineups[0]['startXI'], lineups[0]['substitutes'])
            lineups_final = merge_dicts(lineups_final, players)
        else:
            lineups_final['adversary_formation'] = lineups[1]['formation']
            lineups_final['coach'] = lineups[1]['coach']['name']
            players = get_players('adversary_', lineups[1]['startXI'], lineups[1]['substitutes'])
            lineups_final = merge_dicts(lineups_final, players)

        return lineups_final

    def define_fixture():
        return {
            'team_id': team,
            'team_name': get_team_details(team, fixture['teams'])['name'],
            'team_goals': fixture['goals'][get_team_details(team, fixture['teams'])['play']],
            'team_play_home': get_team_details(team, fixture['teams'])['play_home'],
            'team_penalty': fixture['score']['penalty'][get_team_details(team, fixture['teams'])],
            'team_halftime': fixture['score']['halftime'][get_team_details(team, fixture['teams'])],
            'team_fulltime': fixture['score']['fulltime'][get_team_details(team, fixture['teams'])],
            'team_extratime': fixture['score']['extratime'][get_team_details(team, fixture['teams'])],

            'adversary_id': get_adversary_details(team, fixture['teams'])['id'],
            'adversary_name': get_adversary_details(team, fixture['teams'])['name'],
            'adversary_goals': fixture['goals'][get_adversary_details(team, fixture['teams'])['play']],
            'adversary_penalty': fixture['score']['penalty'][get_adversary_details(team, fixture['teams'])],
            'adversary_halftime': fixture['score']['halftime'][get_adversary_details(team, fixture['teams'])],
            'adversary_fulltime': fixture['score']['fulltime'][get_adversary_details(team, fixture['teams'])],
            'adversary_extratime': fixture['score']['extratime'][get_adversary_details(team, fixture['teams'])],

            'game_date': fixture['fixture']['timestamp'],
            'game_status': fixture['fixture']['status']['long'],
            'game_elapsed': fixture['fixture']['status']['elapsed'],
            'city': fixture['fixture']['venue']['city'],
            'league': fixture['league']['name'],
            'season': fixture['league']['season'],
            'round': fixture['league']['round'],

            'winner': get_team_details(team, fixture['teams'])['winner'],
        }

    fixture_map = define_fixture()
    print(fixture_map)
    statistics_map = define_statistics()
    print(statistics_map)
    result = merge_dicts(fixture_map, statistics_map)
    events_map = define_events()
    print(events_map)
    result = merge_dicts(result, events_map)
    lineups_map = define_lineups()
    print(lineups_map)
    result = merge_dicts(result, lineups_map)

    with open('football.csv', 'w') as f:
        w = csv.DictWriter(f, result.keys())
        w.writeheader()
        w.writerow(result)

    return result


if __name__ == '__main__':
    league = 39
    season = '2022'
    team = 1
    status = 'FT'

    fixture = get_fixtures(league, season, team, status)

    #statistics = get_statistics(fixture[0]['fixture']['id'], team)
    #events = get_events(fixture[0]['fixture']['id'], team)
    #lineups = get_lineups(fixture[0]['fixture']['id'], team)
    #define_csv_final(fixture[0], statistics[0], events, lineups, team)

