#!/usr/bin/env python

'''tournament.py -- implementation of a Swiss-system tournament

The game tournament will use the Swiss system for pairing up
players in each round: players are not eliminated, and each
player should be paired with another player with the same number
of wins, or as close as possible.
'''

import bleach
import psycopg2


def connect():
    '''Connect to the PostgreSQL database.  Returns a database connection.'''
    return psycopg2.connect('dbname=tournament')


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


def countPlayers():
    '''Returns the number of players currently registered.'''
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
    '''Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

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
    '''Returns a list of the players and their win records, sorted by wins.

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


def reportMatch(winner, loser):
    '''Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
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

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

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
