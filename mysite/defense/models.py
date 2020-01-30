from django.db import models
# Create your models here.


class Players(models.Model):
    '''This works it is the model for the database that contains the players
    first and last name as well as an id number.'''
    player_id = models.CharField(max_length=200, primary_key=True)
    player_lname = models.CharField(max_length=200)
    player_fname = models.CharField(max_length=200)

    def __str__(self):
        return self.player_fname + ' ' + self.player_lname


class TeamInfo(models.Model):
    '''This one is for a table that contains Year, Team, Age, Position, Games, Games started
    and ID as a foreign key. Not sure yet how to make joins in the shell with this'''
    year = models.PositiveSmallIntegerField()
    team = models.CharField(max_length=4)
    age = models.IntegerField()
    position = models.CharField(max_length=20)
    g = models.IntegerField()
    gs = models.IntegerField()
    interceptions = models.IntegerField()
    int_yds = models.IntegerField()
    int_td = models.IntegerField()
    pass_def = models.IntegerField()
    ffb = models.IntegerField()
    fr = models.IntegerField()
    fb_yds = models.IntegerField()
    fb_td = models.IntegerField()
    sacks = models.IntegerField()
    solo = models.IntegerField()
    assists = models.IntegerField()
    tfl = models.IntegerField()
    qb_hits = models.IntegerField()
    sfty = models.IntegerField()
    player_id = models.ForeignKey(Players, db_column='player_id', on_delete=models.CASCADE)
