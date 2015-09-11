import sys
import xml.etree.ElementTree as ET
import requests
import html5lib
from workflow import Workflow, web, manager as SerializeManager
from ImageSerializer import PngSerializer


log = None
SerializeManager.register('png', PngSerializer)
s = requests.Session()
s.cookies.set('birthtime', '126259201')
s.cookies.set('lastagecheckage', '1-January-1974')


def get_game_data(appid):
    log.debug('Getting game data for %s' % appid)
    r = s.get("http://store.steampowered.com/app/%s/" % appid)
    dom = html5lib.parse(r.text, namespaceHTMLElements=False)
    is_dlc = dom.find(".//div[@id='game_area_purchase']/div[@class='game_area_dlc_bubble game_area_bubble']")
    is_mac = dom.find(".//span[@class='platform_img mac']")
    return {'dlc': is_dlc is not None,
            'mac': is_mac is not None}


def get_games():

    xml = web.get('http://steamcommunity.com/id/%s/games?tab=all&xml=1' % wf.settings.get('steam_user', None)).text
    root = ET.fromstring(xml.encode('utf-8'))
    games = []
    for game in root.findall('./games/game'):
        appid = game.find('appID').text

        def wrapped():
            return get_game_data(appid)

        data = wf.cached_data('game_%s' % appid, wrapped, max_age=30 * 24 * 60 * 60)
        games.append({
            'id': appid,
            'name': game.find('name').text,
            'logo': game.find('logo').text,
            'dlc': data['dlc'],
            'mac': data['mac']
        })
    return games


def get_game_icon(logo):
    return web.get(logo).content


def main(wf):
    if not wf.settings.get('steam_user', None):
        return 1

    games = wf.cached_data('games_%s' % wf.settings.get('steam_user'), get_games, max_age=12 * 60 * 60)

    # We do this in a seperate loop so that we can change the serializer
    wf.cache_serializer = 'png'
    if games:
        for game in games:
            def wrapped():
                log.debug('%s needs a logo' % game['name'])
                return get_game_icon(game['logo'])
            # Bad pickle!
            wf.cached_data('icon_%s' % game['id'], wrapped, max_age=0)

if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
