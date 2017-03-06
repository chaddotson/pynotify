from pynotify.core import Notification, Notifier
from pytools.twitter.ootb import tweet


class TwitterNotification(Notification):
    def __init__(self, recipients=[], content=""):
        self.recipients = recipients
        self.content = content

    @property
    def payload(self):

        return ", ".join(map(lambda s: "@" + s, self.recipients)) + " - " + self.content


class TwitterNotifier(Notifier):
    def __init__(self, consumer_key="", consumer_secret="", access_key="", access_secret=""):
        self.consumer_key=consumer_key
        self.consumer_secret=consumer_secret
        self.access_key=access_key
        self.access_secret=access_secret

    def send(self, notification: Notification):
        message = notification.payload
        tweet(consumer_key=self.consumer_key,
              consumer_secret=self.consumer_secret,
              access_key=self.access_key,
              access_secret=self.access_secret,
              message=message)
