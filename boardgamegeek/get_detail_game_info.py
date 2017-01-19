import csv
import time

import requests
from bs4 import BeautifulSoup


def get_name_info(tag):
    # get the primary name and total number of names including primary
    # and alternate names.
    names = tag.find_all('name')
    pri_name = tag.find('name', {'primary': 'true'})
    if pri_name:
        pri_name = pri_name.text.encode('utf-8', 'strict')
    else:
        pri_name = 'NaN'

    if names:
        n_names = len(names)
    else:
        n_names = 0

    return pri_name, n_names


def get_type(tag, term):
    # get mechanic , category or subdomain list
    # return a string with each type separated by ;
    finds = tag.find_all(term)
    if finds:
        finds = [find.text for find in finds]
        finds = ','.join(finds).encode('utf-8', 'strict')
    else:
        finds = 'NaN'
    return finds


def get_val(tag, term):
    try:
        val = tag.find(term).text.encode('utf-8', 'strict')
    except:
        val = 'NaN'
    return val


def get_langdep(tag):
    # get the language dependence votes
    polls = tag.find('poll', {'name': 'language_dependence'})
    if int(polls.attrs['totalvotes']) == 0:
        return 'NaN'
    else:
        results = polls.find_all('result')
        votes = []
        for result in results:
            votes.append(result.attrs['numvotes'])
        votes = ','.join(votes)
        return votes


def main():
    with open('ids_for_test.txt') as f:
        ids = [line.strip() for line in f.readlines()]

    base = 'https://www.boardgamegeek.com/xmlapi/boardgame/{}&stats=1'
    split = 30
    with open('games_detail.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('id', 'type', 'name', 'n_names', 'yearpublished',
                         'description', 'minplayers', 'maxplayers',
                         'playingtime', 'minplaytime', 'maxplaytime', 'minage',
                         'mechanic', 'subdomain', 'category', 'lang_dep',
                         'users_rated', 'average_rating',
                         'bayes_average_rating',
                         'total_owners', 'total_traders', 'total_wanters',
                         'total_wishers', 'total_comments',
                         'total_weights', 'average_weight'))

        for i in range(0, len(ids), split):
            url = base.format(','.join(ids[i:i+split]))
            print('Requesting {}'.format(url))
            req = requests.get(url)
            soup = BeautifulSoup(req.content, 'xml')
            items = soup.find_all('boardgame', attrs={'inbound': False})
            for item in items:
                gid = item.attrs['objectid']
                if item.find('boardgameexpansion', {'inbound': 'true'}):
                    gtype = 'expansion'
                else:
                    gtype = 'boardgame'
                gname, num_names = get_name_info(item)
                gyear = get_val(item, 'yearpublished')

                gdescript = get_val(item, 'description')
                gmin = get_val(item, 'minplayers')
                gmax = get_val(item, 'maxplayers')

                gplay = get_val(item, 'playingtime')
                gminplay = get_val(item, 'minplaytime')
                gmaxplay = get_val(item, 'maxplaytime')
                gminage = get_val(item, 'age')

                gmechanic = get_type(item, 'boardgamemechanic')
                gsubdomain = get_type(item, 'boardgamesubdomain')
                gcategory = get_type(item, 'boardgamecategory')
                glangdep = get_langdep(item)

                usersrated = get_val(item.statistics.ratings, 'usersrated')
                avg = get_val(item.statistics.ratings, 'average')
                bayesavg = get_val(item.statistics.ratings, 'bayesaverage')

                owners = get_val(item.statistics.ratings, 'owned')
                traders = get_val(item.statistics.ratings, 'trading')
                wanters = get_val(item.statistics.ratings, 'wanting')
                wishers = get_val(item.statistics.ratings, 'wishing')

                numcomments = get_val(item.statistics.ratings, 'numcomments')
                numweights = get_val(item.statistics.ratings, 'numweights')
                avgweight = get_val(item.statistics.ratings, 'averageweight')

                writer.writerow((gid, gtype, gname, num_names, gyear,
                                 gdescript, gmin, gmax,
                                 gplay, gminplay, gmaxplay, gminage,
                                 gmechanic, gsubdomain, gcategory, glangdep,
                                 usersrated, avg, bayesavg,
                                 owners, traders, wanters, wishers,
                                 numcomments, numweights, avgweight))
            time.sleep(2)

if __name__ == '__main__':
    main()
