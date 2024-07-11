from celery import Celery
from app_config import create_app
from celery import Celery, shared_task
from flask import render_template_string
# import celeryConfig
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

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


@shared_task
def send_mail(context):
    try:
        print("Sending Mail")
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = os.environ.get('EMAIL_USER')
        smtp_password = os.environ.get('EMAIL_PASSWORD')

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        from_email = "support@teamflow.com"
        to_email = context['email']
        subject = context['subject']

        # Construct the path to the HTML file within the templates folder
        template_path = os.path.join(os.getcwd(), 'templates', context['template_name'])

        # Read the HTML file content
        with open(template_path, 'r') as html_file:
            body = html_file.read()

        # send context inside the html file
        body = render_template_string(body, **context)

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Change the MIME type to 'html'
        msg.attach(MIMEText(body, 'html'))

        server.sendmail(from_email, to_email, msg.as_string())

        server.quit()
        return "Mail sent successfully"

    except Exception as e:
        print(e, "error@celery/send_mail")
        return "Failed to send mail"
