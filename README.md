# NSMeldingen

## Route alert for the Nederlandse Spoorwegen in Holland

1. [Set up a developer account with Twitter](https://developer.twitter.com/en/portal/projects-and-apps)
2. Create your applicatie with Twitter
3. Generate an API Key and Secret
4. Generate an Access Token and Secret
5. [Setup an account with Pushover](https://pushover.net)
6. Get your User Key
7. Create a new app
8. Get token api for the app
9. Fill out NSmeldingen_settings.py
10. Setup your own route in NSmeldingen.py. First by adding all the stations on your route to the include_words and then excluding the stations branching from the route. Check the messages posted to Pushover by placing those stations in the exclude_words. This way only you optimal route remains.
11. Create a directory "config" in and create a NSmeldingen.ini file

    [TWITTER]
    APP_KEY = xxxxxxxxxxxxxxx
    APP_SECRET = xxxxxxxxxxxxxxx
    OAUTH_TOKEN = xxxxxxxxxxxxxxx-xxxxxxxxxxxxxxx
    OAUTH_TOKEN_SECRET = xxxxxxxxxxxxxxx
    ACCOUNT = xxxxx
    EXCLUDE_WORDS = xxx,yyy
    INCLUDE_WORDS = zzz,qqq

    [PUSHOVER]
    USER_KEY = xxxxxxxxxxxxxxx
    TOKEN_API = xxxxxxxxxxxxxxx

2021-05-06 13:13:20
