# coding: utf-8

def colorize(message, color='blue'):
  color_codes = dict(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37)
  code = color_codes.get(color, 34)
  msg = '\033[%(code)sm%(message)s\033[0m' % {'code':code, 'message':message}
  # print(msg)
  return msg


def auto_update(dirpath, current_version):
    from gat_games.auto_updater import AutoUpdater
    LATEST_VERSION_URL = 'http://s3.amazonaws.com/gat-runner/latest-version'

    updater = AutoUpdater(dirpath=dirpath)
    os = updater.get_os()

    FILENAMES = ['gat-runner-%(os)s.zip' % dict(os=os)]
    FILES = {}
    for filename in FILENAMES:
        FILES[filename] = 'http://s3.amazonaws.com/gat-runner/%(filename)s' % dict(filename=filename)

    if updater.has_new_version(current_version, LATEST_VERSION_URL):
        updater.auto_update(FILES)


def open_browser(html):
    import tempfile
    import webbrowser
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(html)
    f.flush()
    webbrowser.open_new_tab('file://' + f.name)


def open_replay(game, players, commands):
    print(colorize('Opening replay in the default Web browser', color='yellow'))
    import urllib
    import urllib2
    URL = 'http://www.gatournament.com/challenge/replay/'

    data = urllib.urlencode(dict(game=game, players=players, commands=commands))
    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
    req = urllib2.Request(URL, data, headers)
    try:
        response = urllib2.urlopen(req)
        html = response.read()
        open_browser(html)
    except urllib2.HTTPError as e:
        print(colorize(e.code, color='red'))
        raise e
    except urllib2.URLError as e:
        print(colorize('Can not connect to url %s' % URL, color='red'))
        raise e


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


if __name__ == '__main__':
    import os
    import sys
    import argparse
    import logging


    try:
        from gat_games.game_engine.gat_json import *
        from gat_games import *
        from gat_runner import VERSION
        from gat_runner.languages import CUSTOM_LANGUAGE_VERSIONS
        from gat_runner.runner import play_from_command_line
    except ImportError as e:
        print(os.getcwd())
        print(sys.path)
        raise e

    BEER = '\xF0\x9f\x8d\xba '
    print(colorize('%s - GAT Runner (%s)' % (BEER, VERSION), color='yellow'))

    if '-d' not in sys.argv and '--disable_auto_update' not in sys.argv:
        dirpath = os.path.dirname(os.path.realpath(__file__))
        # __file__ will not be correct inside the executable zip file
        dirpath = rreplace(dirpath, 'gat-runner', '', 1)
        auto_update(dirpath, VERSION)

    LOG_LEVELS = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    SUPPORTED_GAMES = map(lambda cls: cls.__name__, SUPPORTED_GAMES)

    header = """
====================
Examples:

./gat-runner Truco gat-random gat-random
./gat-runner Truco /path/to/your/algorithm gat-random
./gat-runner Truco /path/to/your/algorithm /path/to/your/algorithm
./gat-runner Truco gat-random gat-random -n1 Player1 -n2 Player2
./gat-runner Truco gat-random gat-random -n1 Player1 -n2 Player2 -ll 20
./gat-runner Truco gat-random gat-random -n1 Player1 -n2 Player2 -ll 20 -s 123
====================
"""

    if '-h' in sys.argv or '--help' in sys.argv:
        print(header)

    parser = argparse.ArgumentParser()

    parser.add_argument('game', choices=SUPPORTED_GAMES, help='Name of the game')
    parser.add_argument('algorithm1', help='File path of the GAT algorithm')
    parser.add_argument('algorithm2', default='gat-random', help='File path of another GAT algorithm. If not specified, it will be defined as "gat-random", which is a naive-random included algorithm in the library.')
    parser.add_argument('-d', '--disable_auto_update', action='store_true', help='Disable auto-update.')
    parser.add_argument('-s', '--seed', type=int, help='Random seed to be used in the game. If not specified, it will be used a random seed.')
    parser.add_argument('-l1', '--language1', choices=CUSTOM_LANGUAGE_VERSIONS, default=None, help='Programming Language of the algorithm 1. If not specified, the language will be identified by the file extension.')
    parser.add_argument('-l2', '--language2', choices=CUSTOM_LANGUAGE_VERSIONS, default=None, help='Same as -l1, but for the algorithm 2.')
    parser.add_argument('-n1', '--name1', default='p1', help="Player1's name.")
    parser.add_argument('-n2', '--name2', default='p2', help="Player2's name.")
    parser.add_argument('-ll', '--loglevel', type=int, default=logging.INFO, choices=LOG_LEVELS, help='Log level')
    parser.add_argument('-pl', '--player_log', type=bool, default=False, help="Save player's logs in a separated file.")
    parser.add_argument('--replay', dest='replay', action='store_true')
    parser.add_argument('--no-replay', dest='replay', action='store_false')
    parser.set_defaults(replay=True)

    args = parser.parse_args()

    game_class = eval(args.game)
    print(colorize('::: %s' % args.game, color='blue'))

    game = play_from_command_line(game_class, args.seed,
        filepath1=args.algorithm1,
        name1=args.name1,
        language1=args.language1,

        filepath2=args.algorithm2,
        name2=args.name2,
        language2=args.language2,

        log_level=args.loglevel,
        player_log=args.player_log)
    report = game.summary()
    print(colorize('[Final Result] %s' % report['summary'], color='cyan'))

    if args.replay:
        players = str([str(p) for p in game.players]).replace("'", '"')
        # players = dumps(game.players)
        open_replay(args.game, players, dumps(game.commands))
    print(colorize('%s cheers!' % (BEER,), color='yellow'))
