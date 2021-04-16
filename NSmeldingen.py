# Name: NSmeldingen
# Coder: Marco Janssen (twitter @marc0janssen)
# date: 2016-07-28
# update: 2021-04-16
# version: 1.0.2


# Importing the modules
from twython import Twython, TwythonError
from chump import Application
from datetime import datetime, date
from re import compile
from time import time
from NSmeldingen_settings import (twitter_app_key,
                                  twitter_app_secret,
                                  twitter_oauth_token,
                                  twitter_oauth_token_secret,
                                  pushover_user_key,
                                  pushover_token_api)


# Setting for PushOver
app = Application(pushover_token_api)
user = app.get_user(pushover_user_key)


# Convert UTC times to local times
def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time()
    offset = datetime.fromtimestamp(
        now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


# Let's gather a list of words we DON'T want to send to Pushover
exclude_words = ["Boskoop",
                 "Alphen",
                 "Mariahoeve",
                 "\"Maria hoeve\"",
                 "Dordrecht",
                 "\"Den Haag HS\"",
                 "Leiden",
                 "Rotterdam",
                 "Arhem",
                 "Nijmegen",
                 "Elst",
                 "Hilversum",
                 "\"Den Dolder\"",
                 "Amsterdam",
                 "Amersfoort",
                 "Schiphol",
                 "Bodegraven"]


# And a list of words we WOULD like to send to Pushover
include_words = ["Tiel",
                 "Passewaaij",
                 "Geldermalsen",
                 "Culemborg",
                 "Castellum",
                 "Houten",
                 "Lunetten",
                 "Vaartse Rijn",
                 "Utrecht",
                 "Woerden",
                 "Gouda",
                 "Zoetermeer",
                 "Voorburg",
                 "\"Den Haag\""]


# Get our last known found tweet by ID
# or else create an empty file and set ID to "0"
try:
    id_file = "/app/since_id.txt"
    f = open(id_file, "r")
    sinceid_value = f.readline()
except IOError:
    f = open(id_file, "w+")
    sinceid_value = "0"
finally:
    f.close()


# OR is Twitter's search operator to search for this OR that
# So let's join everything in include_words with an OR!
wanted = " OR ".join(include_words)


# The - is Twitter's search operator for negative keywords
# So we want to prefix every negative keyword with a -
unwanted = " -" + " -".join(exclude_words)


# And finally our list of keywords that we want to search for
# This will search for any words in include_words minus any exclude_words
keywords = "from:NS_online AND (" + wanted + unwanted + ")"


try:
    # This time we want to set our q to search for our keywords
    twitter = Twython(twitter_app_key, twitter_app_secret,
                      twitter_oauth_token, twitter_oauth_token_secret)
    search_results = twitter.search(
        q=keywords, count=25, since_id=sinceid_value)

    blnFirstWriteDone = False

    for tweet in search_results["statuses"]:

        # Record the first found tweet (is the most recent one)
        if not blnFirstWriteDone:
            f = open(id_file, "w")
            f.write(str(tweet["id_str"]))
            f.close()
            blnFirstWriteDone = True

        # Exclude all replies (tweets starting with @xxxxx)
        pattern = compile("^@([A-Za-z0-9_]+)")
        if not pattern.match(tweet["text"]):

            # Get the time of the tweet and
            # convert the UTC to the local time
            tweetdatetime = tweet["created_at"].split()
            tweettime = tweetdatetime[3].split(":")
            utc = datetime.strptime(date.today().strftime(
                "%Y-%m-%d") + " " + tweetdatetime[3], "%Y-%m-%d %H:%M:%S")
            localtime = str(datetime_from_utc_to_local(utc)).split(" ")

            message = user.send_message(
                localtime[1] + " - " + tweet["text"], sound="tugboat")

except TwythonError as e:
    print(e)
    message = user.send_message("ERROR searching for tweets: " + e)
