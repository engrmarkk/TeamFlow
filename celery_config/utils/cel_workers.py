from celery import Celery
from app_config import create_app
from celery import Celery
# import celeryConfig
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = create_app()


def make_celery(app=app):
    """
    As described in the doc
    """
    celery = Celery(
        app.import_name,
        backend=app.config["RESULT_BACKEND"],
        broker=app.config["BROKER_URL"],
    )
    celery.conf.update(app.config)
    # celery.config_from_object(celeryConfig)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery()


@celery.task
def send_mail():
    print("Sending Mail")
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'easytransact.send@gmail.com'
    smtp_password = 'zkfvuazbihvpwvip'

    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)

    from_email = 'easytransact.send@gmail.com'
    to_email = 'adeniyiboladale@yahoo.com'
    subject = 'Celery Test'
    body = 'This is a test email sent from Celery Task in the TeamFlow app.'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(from_email, to_email, msg.as_string())

    server.quit()
