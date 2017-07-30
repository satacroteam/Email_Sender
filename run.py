import smtplib
import argparse

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


class Mailer(object):
    """
    Class to manage email
    """

    def __init__(self, from_mail, server, pwd):
        """
        Object to send mails
        :param from_mail: Email address of the sender
        :type from_mail: String
        :param server: SMTP server [smtplib.SMTP('smtp.gmail.com', 587) for gmail]
        :type server: SMTP object from smtplib
        :param pwd: Password for the sender mail account
        :type from_mail: String
        """
        self.from_mail = from_mail
        self.server = server
        self.pwd = pwd

    def server_connection(self):
        """
        Connection to the SMTP server
        :return: Nothing (only connect)
        """
        self.server.starttls()
        self.server.login(self.from_mail, self.pwd)

    def load_emails(self, filename):
        """
        Load emails from a text file
        :param filename: Path to the text file
        :return: A list of the emails
        """
        return self.load_message(filename).split("\n")

    def send(self, to_mail, subj, mess, pdf=None):
        """
        Function to send mails
        :param to_mail: Email(s) of the recipient(s)
        :param subj: Subject of the mails
        :param mess: Message of the mails
        :param pdf: Path of the attached PDF
        :return: Nothing (just send the mails)
        """
        self.__mail(to_mail, subj, mess, pdf=pdf)

    def __mail(self, to_mail, subj, mess, pdf=None):
        """
        Function to send mails
        :param to_mail: Address mails of the recipient
        :param subj: Subject of the mails
        :param mess: Message of the mails
        :param pdf: Path of the attached PDF
        :return: Nothing (just send the mails)
        """
        # Message header building
        msg = MIMEMultipart()
        msg['From'] = self.from_mail
        msg['To'] = to_mail
        msg['Subject'] = subj

        # Message body building
        body = mess
        msg.attach(MIMEText(body, 'plain'))

        # Message attachment building
        if pdf:
            msg.attach(self.load_pdf(pdf))

        # Convert the message in string
        text = msg.as_string()

        # Send the message
        self.server.sendmail(self.from_mail, to_mail, text)

    def server_disconnection(self):
        """
        Disconnection of the SMTP server
        :return: Nothing (only disconnect)
        """
        self.server.quit()

    @staticmethod
    def load_pdf(filename):
        """
        Format a pdf in order to be sent by mail
        :param filename: Path to the attachment
        :return: Attachment file formatted
        """
        attachment = open(filename, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        return part

    @staticmethod
    def load_message(filename):
        """
        Load message from a text file
        :param filename: Path to the text file
        :return: The message
        """
        return open(filename, "r", encoding="iso-8859-1").read()


if __name__ == '__main__':
    """
    Script to send mail with:
      - message : content of message text file
      - subject : subject of the email (Object)
      - attachment : attachment file such as pdf
    to:
      - emails : list of email of the email text file
    """
    # Define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("u", help="Email address of the sender")
    parser.add_argument("p", help="Password of the sender's email account")
    parser.add_argument("s", help="Subject of the email")
    parser.add_argument("t", help="Text of the email")
    parser.add_argument("d", help="Destination emails")
    parser.add_argument("a", nargs='?', help="Attachment of the mail (optional)")
    args = parser.parse_args()

    # Define the SMTP server object
    server = smtplib.SMTP('smtp.gmail.com', 587)

    # Build the mail manager object
    try:
        mailer = Mailer(from_mail=args.u, server=server, pwd=args.p)
        mailer.server_connection()
    except ValueError:
        print("Oops! Entered values does not fit")

    # Load the message
    message = mailer.load_message(args.t)

    # Load the emails
    emails = mailer.load_emails(args.d)

    # Send message to each emails
    for email in emails:
        print(email)
        mailer.send(email,
                    args.s,
                    message,
                    pdf=args.a)
        
    # Disconnect from the SMTP server
    mailer.server_disconnection()
