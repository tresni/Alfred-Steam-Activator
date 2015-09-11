#!/usr/bin/env python
# encoding: utf-8

import sys
import argparse
import shlex
import pipes
from os.path import exists, expanduser
from workflow import Workflow, ICON_INFO, ICON_WARNING
from workflow.background import run_in_background, is_running

DEFAULT_STEAM_LIBRARY = "~/Library/Application Support/Steam/steamapps/"


def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--installed", action="store_true")
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("-d", "--dlc", action="store_true")
    parser.add_argument("-u", "--user", action="store", type=str, default=None)
    if sys.stdin.isatty():
        (options, query) = parser.parse_known_args(wf.args)
    else:
        (options, query) = parser.parse_known_args(shlex.split(wf.args[0]))

    if options.user:
        wf.settings['steam_user'] = options.user

    if not wf.settings.get('steam_user', None):
        wf.add_item('No steam username set',
                    'Use -u [username] to set your username!',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    query = " ".join(map(lambda x: pipes.quote(x), query))

    if not wf.cached_data_fresh('games_%s' % wf.settings.get('steam_user'), 12 * 60 * 60):
        run_in_background('update', ['/usr/bin/python', wf.workflowfile('background.py')])

    if is_running('update'):
        wf.add_item('Updating Steam games...', icon=ICON_INFO)

    games = wf.cached_data('games_%s' % wf.settings.get('steam_user'), None, max_age=0)

    if games:
        if query:
            games = wf.filter(query, games, key=lambda x: x['name'])

        if not options.dlc:
            games = filter(lambda x: 'dlc' not in x or not x['dlc'], games)

        if not options.all:
            games = filter(lambda x: 'mac' not in x or x['mac'], games)

        if options.installed:
            # This will check the primary steam install location
            # Need to figure out how to parse the libraryfolders.vdf filter to get
            # additional locations.  Appear to be '\t"\d+"\t+"[PATH TO FOLDER]"' lines...
            games = filter(lambda x: exists(expanduser("%s/appmanifest_%s.acf" % (DEFAULT_STEAM_LIBRARY, x['id']))),
                           games)

        for game in games:
                icon = wf.cachefile("icon_%s.png" % game['id'])
                wf.add_item(game['name'],
                            uid=game['id'],
                            valid=True,
                            arg=game['id'],
                            icon=icon if exists(icon) else None)

        if not games:
            wf.add_item('No %smatches%s' % ('installed ' if options.installed else '',
                                            ' for %s' % query if query else ''),
                        'Try searching with --all for all games or --dlc to see DLC',
                        icon=ICON_INFO)
    else:
        if not is_running('update'):
            wf.add_item('Unable to retrieve your games from Steam',
                        'Is your custom URL really "%s"?' % wf.settings.get('steam_user'))
    wf.send_feedback()
    return 0

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
