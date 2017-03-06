from email.mime.text import MIMEText

from pynotify.core import Notification, Notifier
from pytools.email import SMTPSender


class EmailNotification(Notification):
    def __init__(self, originator="", recipients=[], subject="", content=""):
        self.originator = originator
        self.recipients = recipients
        self.subject = subject
        self.content = content

    @property
    def payload(self):
        # msg = MIMEMultipart()
        msg = MIMEText(self.content)

        msg['From'] = self.originator
        msg['To'] = ", ".join(self.recipients)

        if self.subject:
            msg['Subject'] = self.subject

        msg.preamble = "text"

        # msg.preamble = 'image'
        # img = MIMEImage(thumbnail.content, 'jpg')
        # msg.add_header('Content-Disposition', 'attachment', filename='image.jpg')
        # msg.attach(img)
        return msg


class EmailNotifier(Notifier):
    def __init__(self, smtp_host, smtp_port, smtp_username, smtp_password):
        self._smtp = SMTPSender(username=smtp_username, password=smtp_password, server=smtp_host, port=smtp_port)

    def send(self, notification: Notification):
        self._smtp.send(message=notification.payload)