# Name: NSmeldingen
# Coder: Marco Janssen (twitter @marc0janssen)
# date: 2016-07-28
# update: 2021-05-06 10:35:43


# Importing the modules
from twython import Twython, TwythonError
from chump import Application
from datetime import datetime
from re import compile
from time import time
import logging
import configparser
import shutil
import sys


class NSmeldingen():

    def __init__(self):

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

        # Filename to hold the last known TwitterID
        self.id_file = "./config/NSmeldingen_lastID.txt"

        # Get our last known found tweet by ID
        # or else create an empty file and set ID to "0"
        try:
            f = open(self.id_file, "r")
            self.sinceid_value = f.readline()
        except IOError:
            f = open(self.id_file, "w+")
            self.sinceid_value = "0"
        finally:
            f.close()

        self.config_file = "./config/NSmeldingen.ini"

        try:
            with open(self.config_file, "r") as f:
                f.close()
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.config_file)

                self.twitter_app_key = self.config['TWITTER']['APP_KEY']
                self.twitter_app_secret = self.config['TWITTER']['APP_SECRET']
                self.twitter_oauth_token = \
                    self.config['TWITTER']['OAUTH_TOKEN']
                self.twitter_oauth_token_secret = \
                    self.config['TWITTER']['OAUTH_TOKEN_SECRET']
                self.twitter_account = self.config['TWITTER']['ACCOUNT']
                self.exclude_words = list(
                    self.config['TWITTER']['EXCLUDE_WORDS'].split(","))
                self.include_words = list(
                    self.config['TWITTER']['INCLUDE_WORDS'].split(","))

                self.pushover_user_key = self.config['PUSHOVER']['USER_KEY']
                self.pushover_token_api = self.config['PUSHOVER']['TOKEN_API']

            except KeyError:
                logging.error(
                    "Can't get keys from INI file. "
                    "Please check for mistakes."
                )

                sys.exit()

        except IOError or FileNotFoundError:
            logging.error(
                f"Can't open file {self.config_file}, "
                f"creating example INI file."
            )

            shutil.copyfile('./app/NSmeldingen.ini.example',
                            './config/NSmeldingen.ini.example')
            sys.exit()

    # Convert UTC times to local times
    def datetime_from_utc_to_local(self, utc_datetime):
        now_timestamp = time()
        offset = datetime.fromtimestamp(
            now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset

    # convert a tweetdatetime to datetime_utc
    def tweetdatetime_to_datetime_utc(self, tweetDate):

        return datetime.strptime(
            tweetDate, "%a %b %d %H:%M:%S +0000 %Y"
        )

    def run(self):
        # Setting for PushOver
        self.appPushover = Application(self.pushover_token_api)
        self.userPushover = self.appPushover.get_user(self.pushover_user_key)

        # OR is Twitter's search operator to search for this OR that
        # So let's join everything in include_words with an OR!
        self.wanted = " OR ".join(self.include_words)

        # The - is Twitter's search operator for negative keywords
        # So we want to prefix every negative keyword with a -
        self.unwanted = " -" + " -".join(self.exclude_words)

        # And finally our list of keywords that we want to search for
        # This will search for any words in include_words
        # minus any exclude_words
        self.keywords = (
            f"from:{self.twitter_account} AND "
            f"({self.wanted}{self.unwanted})"
        )

        print(self.keywords)

        try:
            # This time we want to set our q to search for our keywords
            self.twitter = Twython(
                self.twitter_app_key,
                self.twitter_app_secret,
                self.twitter_oauth_token,
                self.twitter_oauth_token_secret
            )
            self.search_results = self.twitter.search(
                q=self.keywords, count=25, since_id=self.sinceid_value)

            self.blnFirstWriteDone = False

            for tweet in self.search_results["statuses"]:

                # Record the first found tweet (is the most recent one)
                if not self.blnFirstWriteDone:
                    f = open(self.id_file, "w")
                    f.write(str(tweet["id_str"]))
                    f.close()
                    self.blnFirstWriteDone = True

                # Exclude all replies (tweets starting with @xxxxx)
                self.pattern = compile("^@([A-Za-z0-9_]+)")
                if not self.pattern.match(tweet["text"]):

                    # Get the time of the tweet and
                    # convert the UTC to the local time

                    self.localtime = datetime.strftime(
                        (
                            self.datetime_from_utc_to_local(
                                self.tweetdatetime_to_datetime_utc(
                                    tweet["created_at"])
                            )
                        ),
                        "%H:%M:%S",
                    )

                    self.localdate = datetime.strftime(
                        (
                            self.datetime_from_utc_to_local(
                                self.tweetdatetime_to_datetime_utc(
                                    tweet["created_at"])
                            )
                        ),
                        "%Y-%m-%d",
                    )

                    if self.localdate == datetime.strftime(
                        datetime.now(), "%Y-%m-%d"
                    ):

                        self.message = self.userPushover.send_message(
                            f"{self.localtime} - {tweet['text']}', "
                            f"sound='tugboat'"
                        )

        except TwythonError as e:
            print(e)


if __name__ == '__main__':

    nsmeldingen = NSmeldingen()
    nsmeldingen.run()
    nsmeldingen = None
