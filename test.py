import requests
import csv

# api-endpoint
URL = 'https://api-football-v1.p.rapidapi.com/v3'

headers = {
    'X-RapidAPI-Key': '3f9643edf1msh2b477fef8031f74p1bcea3jsn23e47105c015',
    'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
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
    params = {
        'fixture': fixture,
        'team': team,
    }
    r = requests.get(url=URL + '/fixtures/events', params=params, headers=headers)

    data = r.json()
    print(data)
    return data


def get_lineups(fixture, team):
    params = {
        'fixture': fixture,
        'team': team,
    }

    r = requests.get(url=URL + '/fixtures/lineups', params=params, headers=headers)

    data = r.json()
    print(data)
    return data


def get_statistics(fixture, team):
    params = {
        'fixture': fixture,
        'team': team,
    }

    r = requests.get(url=URL + '/fixtures/statistics', params=params, headers=headers)

    data = r.json()
    print(data)
    return data


def get_fixtures(league, season, team, status):
    params = {
        'league': league,
        'season': season,
        'team': team,
        'status': status
    }
    query_params = '?league=' + league + \
                   '&season=' + season + \
                   '&team=' + team + \
                   '&status=' + status

    r = requests.get(url=URL + '/fixtures', params=params, headers=headers)
    print(r.status_code)
    data = r.json()
    print(data)
    return data


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
                substitutes_map[team_info + 'substitute_pos' + str(substitute['player']['pos']) + 'substitute_grid_' +
                                str(substitute['player']['grid'])] = str(substitute['player']['name'])

            for player in start_players:
                players_map[team_info + 'player_pos' + str(player['player']['pos']) + 'player_grid_' +
                            str(player['player']['grid'])] = str(player['player']['name'])

            return merge_dicts(players_map, substitutes_map)

        lineups_team_a = {}
        lineups_team_b = {}

        lineups_team_a['team_formation'] = lineups[0]['formation']
        lineups_team_a['coach'] = lineups[0]['coach']['name']
        players_team_1 = get_players('team_', lineups[0]['startXI'], lineups[0]['substitutes'])
        lineups_team_a = merge_dicts(lineups_team_a, players_team_1)

        lineups_team_b['adversary_formation'] = lineups[1]['formation']
        lineups_team_b['coach'] = lineups[1]['coach']['name']
        players_team_2 = get_players('adversary_', lineups[1]['startXI'], lineups[1]['substitutes'])
        lineups_team_b = merge_dicts(lineups_team_b, players_team_2)

        return merge_dicts(lineups_team_a, lineups_team_b)

    def define_fixture():
        play_where = get_team_details(team, fixture['teams'])['play']
        play_adversary_where = get_adversary_details(team, fixture['teams'])['play']
        main_team_winner = get_team_details(team, fixture['teams'])['winner']
        adversary_team_winner = get_team_details(team, fixture['teams'])['winner']

        winner = ''

        if main_team_winner is None:
            if adversary_team_winner is None:
                winner = 'tie'
            else:
                winner = 'loser'
        else:
            winner = 'winner'

        return {
            'team_id': team,
            'team_name': get_team_details(team, fixture['teams'])['name'],
            'team_goals': fixture['goals'][get_team_details(team, fixture['teams'])['play']],
            'team_play_where': play_where,
            'team_penalty': fixture['score']['penalty'][play_where],
            'team_halftime': fixture['score']['halftime'][play_where],
            'team_fulltime': fixture['score']['fulltime'][play_where],
            'team_extratime': fixture['score']['extratime'][play_where],

            'adversary_id': get_adversary_details(team, fixture['teams'])['id'],
            'adversary_name': get_adversary_details(team, fixture['teams'])['name'],
            'adversary_goals': fixture['goals'][get_adversary_details(team, fixture['teams'])['play']],
            'adversary_play_where': play_adversary_where,
            'adversary_penalty': fixture['score']['penalty'][play_adversary_where],
            'adversary_halftime': fixture['score']['halftime'][play_adversary_where],
            'adversary_fulltime': fixture['score']['fulltime'][play_adversary_where],
            'adversary_extratime': fixture['score']['extratime'][play_adversary_where],

            'game_date': fixture['fixture']['timestamp'],
            'game_status': fixture['fixture']['status']['long'],
            'game_elapsed': fixture['fixture']['status']['elapsed'],
            'city': fixture['fixture']['venue']['city'],
            'league': fixture['league']['name'],
            'season': fixture['league']['season'],
            'round': fixture['league']['round'],

            'winner': winner,
        }

    fixture_map = define_fixture()
    statistics_map = define_statistics()
    result = merge_dicts(fixture_map, statistics_map)
    events_map = define_events()
    result = merge_dicts(result, events_map)
    lineups_map = define_lineups()
    result = merge_dicts(result, lineups_map)

    with open('liverpool_fixture_' + str(fixture['fixture']['id']) + '.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, result.keys())
        w.writeheader()
        w.writerow(result)

    return result


if __name__ == '__main__':
    league = '39'
    season = '2022'
    team = '40'
    status = 'FT'

    fixture = get_fixtures(league, season, team, status)

    statistics = get_statistics(fixture['response'][0]['fixture']['id'], team)
    events = get_events(fixture['response'][0]['fixture']['id'], team)
    lineups_team_1 = get_lineups(fixture['response'][0]['fixture']['id'], team)
    lineups_team_2 = get_lineups(fixture['response'][0]['fixture']['id'], get_adversary_details(team, fixture['response'][0]['teams'])['id'])
    define_csv_final(fixture['response'][0], statistics['response'][0],
                     events['response'], [lineups_team_1['response'][0], lineups_team_2['response'][0]], team)
