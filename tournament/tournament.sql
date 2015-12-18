-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE if exists tournament;
CREATE DATABASE tournament;
\c tournament
CREATE TABLE players (
    id serial primary key,
    name text
);
CREATE TABLE tournaments (
    id serial primary key,
    winner int references players(id)
);
ALTER TABLE players
ADD present_tournament int references tournaments(id);
CREATE TABLE matches (
    id serial primary key,
    tournament int references tournaments(id),
    winner int references players(id),
    loser int references players(id)
);
--
-- Views
--
-- Used for easy access without duplicating queries in backend code.
-- However, these queries are not cached and execute at runtime.
--
-- The number of matches won by a player
CREATE VIEW numwins AS
SELECT winrecords.id, count(winrecords.winner) AS wins FROM
(
    SELECT a.id, a.name, w.winner FROM players a
    LEFT JOIN matches w
    ON a.id = w.winner
) AS winrecords
GROUP BY winrecords.id;
-- The number of matches played by a player
CREATE VIEW nummatches AS
SELECT a.id, count(w.loser) as matches FROM players a
LEFT JOIN matches w
ON a.id = w.winner OR a.id = w.loser
GROUP BY a.id;
-- A stats view for player ID name, wins and total matches
CREATE VIEW statistics AS
SELECT people.id, people.name, stats.wins, stats.matches FROM
(
    SELECT a.id, a.wins, b.matches FROM numwins a
    LEFT JOIN nummatches b ON a.id = b.id
) stats LEFT JOIN players people
ON people.id = stats.id;
