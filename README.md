# swiss_tournament
Python Backend for Swiss Tournament - Originally for Udacity Intro to Relational Databases

## Vagrant

This project come with a Vagrant development environment. You will need to
have git and VirtualBox installed.

### Getting the source for Vagrant

Once you have git and VirtualBox installed, to get up and running:

`git clone https://github.com/bryanapperson/swiss_tournament/tree/master`

`cd swiss_tournament`

* For single tournament support only (Udacity project):

`git checkout single_tournament`

* For multi-tournament (extra credit in the Udacity project):

`git checkout master`

For the latest version use the `master` branch.

### Starting the Vagrant instance

To start the Vagrant instance:

`vagrant up`

Then, to connect to the instance:

`vagrant ssh`

### Running the Unit Tests

To run the unit tests from within the vagrant VM:

`cd /vagrant/tournament`

First the database must be created. To do this:

`psql -f tournament.sql`

To execute the unit tests:

`python tournament_test.py`

* The test script will exit without error if all unit tests are passed.

## Function documentation

For documentation on tournament.py, use pydoc. It will format the docstrings for easy to view output.
