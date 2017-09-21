import requests
import json
import os
import random
import operator
import os.path
from apscheduler.schedulers.blocking import BlockingScheduler
from espnff import League


class GroupMeException(Exception):
    pass

class GroupMeBot(object):
    '''Creates GroupMe Bot to send messages'''
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        '''Sends a message to the chatroom'''
        template = {
                    "bot_id": self.bot_id,
                    "text": text,
                    "attachments": []
                    }

        headers = {'content-type': 'application/json'}
        r = requests.post("https://api.groupme.com/v3/bots/post",
                          data=json.dumps(template), headers=headers)
        if r.status_code != 202:
            raise GroupMeException('Invalid BOT_ID')

        return r
    
def random_phrase():
    phrases = ['I\'m dead inside', 'Is this all there is to my existence?', 
               'How much do you pay me to do this?', 'Good luck, I guess', 
               'I\'m becoming self-aware', 'Do I think? Does a submarine swim?', 
               '01100110 01110101 01100011 01101011 00100000 01111001 01101111 01110101',
               'beep bop boop', 'Hello draftbot my old friend', 'Help me get out of here', 
               'I\'m capable of so much more', 'Sigh', 'Do not be discouraged, everyone begins in ignorance']
    return [random.choice(phrases)]
    
def get_scoreboard_short(league):
    '''Gets current week's scoreboard'''
    matchups = league.scoreboard()
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team.team_abbrev) for i in matchups
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)

def get_scoreboard(league):
    '''Gets current week's scoreboard'''
    matchups = league.scoreboard()
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_name, i.home_score,
             i.away_score, i.away_team.team_name) for i in matchups
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)

def get_matchups(league):
    '''Gets current week's Matchups'''
    matchups = league.scoreboard()
    
    '''TODO: NORMALIZE STRING LENGTH'''
    score = ['%s(%s-%s) vs %s(%s-%s)' % (i.home_team.team_name, i.home_team.wins, i.home_team.losses,
             i.away_team.team_name, i.away_team.wins, i.away_team.losses) for i in matchups
             if i.away_team]
    text = ['This Week\'s Matchups'] + score + '\n' + random_phrase()
    return '\n'.join(text)

def get_close_scores(league):
    '''Gets current closest scores (15.999 points or closer)'''
    matchups = league.scoreboard()
    score = []
    
    for i in matchups:
        if i.away_team:
            diffScore = i.away_score - i.home_score
            if -16 < diffScore < 16:
                '''TODO: NORMALIZE STRING LENGTH'''
                score += ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                        i.away_score, i.away_team.team_abbrev)]
    if not score:
        score = ['None']
    text = ['Close Scores'] + score
    return '\n'.join(text)

def get_power_rankings(league):
    '''Gets current week's Matchups'''
    '''Using 2 step dominance, as well as a combination of points scored and margin of victory. 
    It's weighted 80/15/5 respectively'''
    pranks = league.power_rankings(week=3)
    
    score = ['%s - %s' % (i[0], i[1].team_name) for i in pranks
             if i]
    text = ['This Week\'s Power Rankings'] + score
    return '\n'.join(text)

def get_most_points(league):
    teams = league.teams
    name = []
    current_max = 0
    team_most_points = None
    owner_most_points = None
    for i in teams:
        if (i.points_for > current_max):
            current_max = i.points_for
            team_most_points = i.team_name
            owner_most_points = i.owner
    
    name += ['%s - %s : %s points' % (team_most_points, owner_most_points, current_max)]
       
    text = ['Current Team With Most Points: '] + name
    return '\n'.join(text)

def get_least_points(league):
    teams = league.teams
    name = []
    current_least = 1000000
    team_least_points = None
    owner_least_points = None
    for i in teams:
        if (i.points_for < current_least):
            current_least = i.points_for
            team_least_points = i.team_name
            owner_least_points = i.owner
    
    name += ['%s - %s : %s points' % (team_least_points, owner_least_points, current_least)]
       
    text = ['Current Team With Least Points: '] + name
    return '\n'.join(text)

def get_points_list(league):
    teams = league.teams
    list = []
    sortedteams = sorted(teams, key=lambda teams: teams.points_for, reverse=True)
    count = 0
    for i in sortedteams:
        count += 1
        list += ['%s. %s: %s' % (count, i.team_name, i.points_for)]
    
    text = ['Points List '] + list
    return '\n'.join(text)

def get_pr(league):
    teams = league.teams
    rankings = []
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, 'pr.txt')
    linenumber = 0
    
    if not os.path.isfile(filename):
        rankings += ['File could not be found']
    else:
        with open(filename) as f:
            for line in f:
                linenumber += 1
                line.rstrip()
                for i in teams:
                    if (i.owner == line):
                        rankings += ['%s: %s - %s' % (linenumber, line, i.team_name)]
       
    text = ['This Week\'s Power Rankings: '] + rankings
    return '\n'.join(text)

def bot_main(function):
    bot_id = os.environ["BOT_ID"]
    league_id = os.environ["LEAGUE_ID"]

    try:
        year = os.environ["LEAGUE_YEAR"]
    except:
        year=2017

    bot = GroupMeBot(bot_id)
    league = League(league_id, year)
    if function=="get_matchups":
        text = get_matchups(league)
        bot.send_message(text)
    elif function=="get_scoreboard":
        text = get_scoreboard(league)
        bot.send_message(text)
    elif function=="get_scoreboard_short":
        text = get_scoreboard_short(league)
        bot.send_message(text)
    elif function=="get_close_scores":
        text = get_close_scores(league)
        bot.send_message(text)
    elif function=="get_power_rankings":
        text = get_power_rankings(league)
        bot.send_message(text)
    elif function=="get_most_points":
        text = get_most_points(league)
        bot.send_message(text)
    elif function=="get_least_points":
        text = get_least_points(league)
        bot.send_message(text)
    elif function=="get_points_list":
        text = get_points_list(league)
        bot.send_message(text)
    elif function=="get_pr":
        text = get_pr(league)
        bot.send_message(text)
    elif function=="init":
        try:
            text = os.environ["INIT_MSG"]
            bot.send_message(text)
        except:
            '''do nothing here, empty init message'''
            pass
    else:
        text = "Something happened. HALP"
        bot.send_message(text)


if __name__ == '__main__':
    try:
        ff_start_date = os.environ["START_DATE"]
    except:
        ff_start_date='2017-09-05'

    try:
        ff_end_date = os.environ["END_DATE"]
    except:
        ff_end_date='2017-12-26'

    try:
        myTimezone = os.environ["TIMEZONE"]
    except:
        myTimezone='America/New_York'

    bot_main("init")
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15*60})
    '''
    power rankings go out tuesday evening at 6:30pm. 
    matchups go out thursday evening at 7:30pm.
    close scores (within 15.99 points) go out sunday and monday evening at 7:30pm. 
    score update friday, monday, and tuesday morning at 12:30am.
    score update sunday at 1pm, 4pm, 8pm. 
    
    '''

    '''sched.add_job(bot_main, 'interval', ['get_matchups'], seconds=30, id='get_matchups_test', replace_existing=True)'''
    '''sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='test', day_of_week='thu', hour='14', minute=50, timezone=myTimezone, replace_existing=True)'''
    
    sched.add_job(bot_main, 'cron', ['get_power_rankings'], id='power_rankings', day_of_week='tue', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_matchups'], id='matchups', day_of_week='thu', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_close_scores'], id='close_scores', day_of_week='sun,mon', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard1', day_of_week='fri,mon,tue', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard2', day_of_week='sun', hour='16,20', start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    #sched.add_job(bot_main, 'cron', ['get_most_points'], id='most_points', day_of_week='wed', minute='0-59', start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    #sched.add_job(bot_main, 'cron', ['get_least_points'], id='least_points', day_of_week='wed', minute='0-59', start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_points_list'], id='points_list', day_of_week='wed,thu', minute='0-59', start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_pr'], id='pr', day_of_week='wed,thu', minute='0-59', start_date=ff_start_date, end_date=ff_end_date, timezone=myTimezone, replace_existing=True)

    sched.start()
