#!/usr/bin/env python

'''tournament.py -- implementation of a Swiss-system tournament

The game tournament will use the Swiss system for pairing up
players in each round: players are not eliminated, and each
player should be paired with another player with the same number
of wins, or as close as possible.
'''

import bleach
import ConfigParser
import logging
import psycopg2


# Logging utility

def create_logger():
    '''Creates logger object for module.

    Creates and returns logger module.
    '''
    logger = logging.getLogger(__name__)
    return logger

LOGGER = create_logger()


def create_debug(dbgstr):
    '''Creates debug level log messages

    Creates debug message <dbgstr> in the log if log level is set to debug.
    '''
    LOGGER.debug(str(dbgstr))


def create_info(infostr, boolp=False):
    '''Creates info level log messages

    Creates info message <infostr> in the log if log level is set to info,
    prints if boolp is True.
    '''
    if boolp is True:
        print ('Info: ' + str(infostr))
    LOGGER.info(str(infostr))


def create_warning(warnstr, boolp=True):
    '''Creates warning level log messages

    Creates warning message <warnstr> in the log if log level is set to warn,
    prints if boolp is True.
    '''
    if boolp is True:
        print ('Warning: ' + str(warnstr))
    LOGGER.warning(str(warnstr))


def create_exception(errstr):
    '''Creates exceptions and exeption level log messages

    Raises exception, prints <errstr> - logs errstr if loglevel is set to
    error.
    '''
    print ('Error: ' + str(errstr))
    LOGGER.error(errstr)
    raise Exception(str(errstr))


def configure_logger(loglevel='WARNING'):
    '''Configures log level

    Returns a numeric log level assuming loglevel is bound to the string value
    obtained from the function argument.

    Args:
        loglevel:
            type: string
            description: string representing log lvel for python logging module
                         defaults to WARNING.
            valid inputs: DEBUG, ERROR, WARNING, INFO
    '''
    numericlevel = getattr(logging, loglevel.upper(), None)
    if not isinstance(numericlevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    return numericlevel

# End logging utility

# Config utility

def read_config(configfile):
    '''Parses the config file

    Parses the config file and returns the configuration as an object

    Args:
        configfile:
            type: string
            description: configuration file
    '''
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    return config


def config_section_map(configuration, section='default'):
    '''Maps sections of configuration file

    Returns a section of the configuration object as a dictionary

    Args:
        configuration:
            type: object
            description: returned object from function read_config
        section:
            type: string
            description: section of object to parse, defaults to default
    '''
    configdict = {}
    options = configuration.options(section)
    for option in options:
        try:
            configdict[option] = configuration.get(section, option)
            if configdict[option] == -1:
                create_debug("skip: %s" % option)
        except Exception:
            print("exception on %s!" % option)
            configdict[option] = None
    return configdict

# End config utility

# Global functions


def connect():
    '''Connect to the PostgreSQL database.  Returns a database connection.'''
    return psycopg2.connect('dbname=tournament')


def deletePlayers():
    '''Remove all the player records from the database.'''
    # Connect to DB
    db = connect()
    # Get cursor
    cursor = db.cursor()
    # Cascade foreign key dependecies
    cursor.execute('TRUNCATE players CASCADE')
    # Commit changes to DB
    db.commit()
    # Close connection
    db.close()


def deleteMatches():
    '''Remove all the match records from the database.'''
    # Connect to DB
    db = connect()
    # Get cursor
    cursor = db.cursor()
    # Cascade foreign key dependecies
    cursor.execute('TRUNCATE matches CASCADE')
    # Commit changes to DB
    db.commit()
    # Close connection
    db.close()


def deleteTournaments():
    '''Remove all the tournament records from the database.'''
    # Connect to DB
    db = connect()
    # Get cursor
    cursor = db.cursor()
    # Cascade foreign key dependecies
    cursor.execute('TRUNCATE tournaments CASCADE')
    # Commit changes to DB
    db.commit()
    # Close connection
    db.close()


def countPlayers():
    '''Returns the number of players currently registered golbally.'''
    # Connect to DB
    db = connect()
    # Get cursor
    cursor = db.cursor()
    # We need a count of rows or to return 0 on none
    player_count = '''
                   SELECT COUNT(id) as num FROM players
                   '''
    cursor.execute(player_count)
    rowcount = cursor.fetchone()
    # Get the first element of tuple
    playernum = rowcount[0]
    # Close connection
    db.close()
    # Return number of players
    return playernum


def registerPlayer(name):
    '''Adds a player to the global tournament database.

    The database assigns a unique serial id number for the player. This
    registers the player without registering them for a perticular tournament.

    Args:
      name: the player's full name (need not be unique).
    '''
    # Sanitize SQL injection vulnerability
    name = bleach.clean(name)
    # Connect to DB
    db = connect()
    # Get cursor
    cursor = db.cursor()
    cursor.execute('INSERT INTO players (name) VALUES (%s)', (name,))
    # Commit changes to DB
    db.commit()
    # Close connection
    db.close()


def playerStandings():
    '''Returns a global list of players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    '''
    # Connect to DB
    db = connect()
    # Get cursor
    cursor = db.cursor()
    # SELECT a.id, count(a.id) as matches FROM players a LEFT JOIN matches w
    # ON a.id = w.winner OR a.id = w.loser GROUP BY a.id;
    # We need a count of rows or to return 0 on none
    player_count = '''
                   SELECT * FROM statistics
                   ORDER BY wins DESC
                   '''
    cursor.execute(player_count)
    stats = cursor.fetchall()
    # Unlikely SQL injection - but still
    # Close connection
    db.close()
    # Return number of players
    return stats


def get_id(t_id=None):
    '''Returns the ID of this tournament

    Returns the ID of the next tournament if arg <t_id> is none, otherwise
    returns input of arg <t_id>
    '''
    if t_id is None:
        pass
    return t_id

# End global functions


class swissTournament(object):
    '''Represents a swiss tournament

    Creates a new swissTournament object representing a swiss tournament.

    Args:
        tournament_id: Defaults to none, in which case a new tournament is
        created in the DB. Supported value is an integer referencing an
        existing tournament in the DB to perform actions on.
    '''
    def __init__(self, tournament_id=None):
        self.id = get_id(tournament_id)

    def countTPlayers(self):
        '''Returns the number of players currently registered for this

        tournament.
        '''
        # Connect to DB
        db = connect()
        # Get cursor
        cursor = db.cursor()
        # We need a count of rows or to return 0 on none
        player_count = '''
                       SELECT COUNT(id) as num FROM players
                       '''
        cursor.execute(player_count)
        rowcount = cursor.fetchone()
        # Get the first element of tuple
        playernum = rowcount[0]
        # Close connection
        db.close()
        # Return number of players
        return playernum

    def registerTPlayer(self, name):
        '''Adds player to the tournament db or updates record for this tournament.

        Args:
            name: the player's full name (need not be unique).
        '''
        # Sanitize SQL injection vulnerability
        name = bleach.clean(name)
        # Connect to DB
        db = connect()
        # Get cursor
        cursor = db.cursor()
        cursor.execute('INSERT INTO players (name) VALUES (%s)', (name,))
        # Commit changes to DB
        db.commit()
        # Close connection
        db.close()

    def playerTStandings(self):
        '''Returns for this tournament:

        A list of players and win records, sorted by wins.
        The first entry in the list should be the player in first place, or a
        player tied for first place if there is currently a tie.

        Returns:
        A list of tuples, each of which contains (id, name, wins, matches):
            id: the player's unique id (assigned by the database)
            name: the player's full name (as registered)
            wins: the number of matches the player has won
            matches: the number of matches the player has played
        '''
        # Connect to DB
        db = connect()
        # Get cursor
        cursor = db.cursor()
        # We need a count of rows or to return 0 on none
        player_count = '''
                       SELECT * FROM statistics
                       ORDER BY wins DESC
                       '''
        cursor.execute(player_count)
        stats = cursor.fetchall()
        # Unlikely SQL injection - but still
        # Close connection
        db.close()
        # Return number of players
        return stats

    def reportMatch(winner, loser, draw=None):
        '''Records the outcome of a single match between two players.

        Args:
            winner:  the id number of the player who won
            loser:  the id number of the player who lost
            draw: defaults to none, if set to True - winner and loser are
                  entered into the DB as winners to support a draw
        '''
        # Sanitize SQL injection vulnerability
        winner = bleach.clean(winner)
        loser = bleach.clean(loser)
        # Connect to DB
        db = connect()
        # Get cursor
        cursor = db.cursor()
        cursor.execute('INSERT INTO matches (winner,loser) VALUES (%s,%s)',
                       (winner, loser))
        # Commit changes to DB
        db.commit()
        # Close connection
        db.close()

    def swissPairings():
        '''Returns a list of pairs of players for the next round of a match.

        Assuming that there are an even number of players registered, each
        player appears exactly once in the pairings.  Each player is paired
        with another player with an equal or nearly-equal win record, that is,
        a player adjacent to him or her in the standings.

        Returns:
        A list of tuples, each of which contains (id1, name1, id2, name2)
            id1: the first player's unique id
            name1: the first player's name
            id2: the second player's unique id
            name2: the second player's name
        '''
        player_ranks = playerStandings()
        pairings = []
        pair = []
        for player in range(0, len(player_ranks)):
            player_info = player_ranks[player]
            if len(pair) == 0:
                pair.append(player_info[0])
                pair.append(player_info[1])
            else:
                pair.append(player_info[0])
                pair.append(player_info[1])
                pair_info = (pair[0], pair[1], pair[2], pair[3])
                pairings.append(pair_info)
                pair = []
        return pairings
