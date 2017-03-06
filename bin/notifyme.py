
from argparse import ArgumentParser
from configparser import ConfigParser, Error as ConfigParserError
from logging import getLogger, basicConfig, DEBUG
from os import environ, getcwd
from os.path import join

from pynotify import EmailNotification, EmailNotifier, TwitterNotification, TwitterNotifier


logger = getLogger(__name__)


def create_ini(filename):
    config = ConfigParser()

    config.add_section("me")
    config.set("me", "hashtags", "")
    config.set("me", "max_results", "10")

    config.add_section("email")
    config.set("email", "smtp_username", "")
    config.set("email", "smtp_password", "")
    config.set("email", "smtp_server", "")
    config.set("email", "smtp_port", "")


    config.add_section("twitter")
    config.set("twitter", "consumer_key", "")
    config.set("twitter", "consumer_secret", "")
    config.set("twitter", "access_key", "")
    config.set("twitter", "access_secret", "")

    with open(filename, "w") as f:
        config.write(f)


default_settings_file = environ.get("NOTIFY_ME")

if default_settings_file:
    default_settings_file = join(default_settings_file, "settings.ini")
else:
    default_settings_file = join(getcwd(), "settings.ini")


def parse_args():
    parser = ArgumentParser(description='pynotify')
    parser.add_argument('--settings', help='Settings file', default=default_settings_file) # nargs='?',
    parser.add_argument('-c', '--create', help='Create settings file', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose logs', default=False, action='store_true')
    parser.add_argument('-e', '--email', help='Notify me via email', default=False, action='store_true')
    parser.add_argument('-t', '--twitter', help='Notify me via twitter', default=False, action='store_true')
    parser.add_argument('--dry-run', dest='dryrun', help="Don't actually notify anyone", default=False, action='store_true')
    parser.add_argument('message', help='Message', nargs='?', type=str, default="")
    parser.add_argument('-i', '--input', help='Capture from stdin', default=False, action='store_true')
    parser.add_argument('--subject', help='Subject (if applicable)', type=str, default="")

    return parser.parse_args()


def read_config_file(filename):
    logger.debug("Reading config file, %s", filename)

    config = ConfigParser()
    config.read(filename)

    logger.debug("Read config file")

    return config


class FailedToBuildEmailNotifier(RuntimeError):
    pass


def build_email_notifier(config):

    try:
        username = config.get("email", "smtp_username")
        password = config.get("email", "smtp_password")
        server = config.get("email", "smtp_server")
        port = config.getint("email", "smtp_port")

    except ConfigParserError as e:
        logger.exception("Failed to read smtp settings from config file. %s", e.message)
        raise FailedToBuildEmailNotifier()

    return EmailNotifier(smtp_host=server, smtp_port=port,
                         smtp_username=username, smtp_password=password)


class FailedToBuildTwitterNotifier(RuntimeError):
    pass


def build_twitter_notifier(config):
    try:
        consumer_key = config.get("twitter", "consumer_key")
        consumer_secret = config.get("twitter", "consumer_secret")
        access_key = config.get("twitter", "access_key")
        access_secret = config.get("twitter", "access_secret")

    except ConfigParserError as e:
        logger.exception("Failed to read smtp settings from config file. %s", e.message)
        raise FailedToBuildTwitterNotifier()

    return TwitterNotifier(consumer_secret=consumer_secret, consumer_key=consumer_key,
                           access_secret=access_secret, access_key=access_key)


def run(args):
    logging_config = dict(level=DEBUG,
                          format='[%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s] %(message)s')
    basicConfig(**logging_config)

    config = read_config_file(args.settings)

    message = args.message

    if args.input:
        from sys import stdin
        for line in stdin.readlines():
            message += line

    if args.email:
        logger.info("Using e-mail notifier")
        email_notifier = build_email_notifier(config)
        subject = args.subject if not args.subject == "" else args.message[:10]
        email = EmailNotification(originator=config.get("email", "sender_email"), recipients=[config.get("me", "email")],
                                  subject=subject, content=message)

        if not args.dryrun:
            logger.info("Sending notification")
            email_notifier.send(email)
        else:
            logger.info("Dry run, not sending notification")

    if args.twitter:
        logger.info("Using twitter notifier")
        twitter_notifier = build_twitter_notifier(config)
        tweet = TwitterNotification(recipients=[config.get("me", "twitter")], content=message)

        if not args.dryrun:
            logger.info("Sending notification")
            twitter_notifier.send(tweet)
        else:
            logger.info("Dry run, not sending notification")


def main():
    args = parse_args()
    if args.verbose:
        getLogger('').setLevel(DEBUG)

    if not args.create:
        run(args)
    else:
        create_ini(args.settings)


if __name__ == "__main__":
    main()



