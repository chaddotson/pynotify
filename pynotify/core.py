
class Notification(object):
    @property
    def payload(self):
        pass


class Notifier(object):
    def send(self, message: Notification):
        pass
