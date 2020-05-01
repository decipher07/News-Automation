import requests 
import redis 
from bs4 import BeautifulSoup 
from secrets import password
import datetime

class Scrapper :
    def __init__(self, keywords):
        self.markup = requests.get('https://news.ycombinator.com/').text
        self.keywords = keywords
    
    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll("a", {"class": "storylink"})
        self.saved_links = [] 
        for link in links:
            for keyword in self.keywords:
                if keyword in link.text:
                    self.saved_links.append(link)
    
    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        for link in self.saved_links:
            r.set(link.text, str(link)) 

    def email(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        links = [r.get(k) for k in r.keys()]

        #Email
        import smtplib

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # me == my email address
        # you == recipient's email address
        fromEmail = "newfeeder@gmail.com"
        toEmail = "xavewox292@tgres24.com"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = fromEmail 
        msg['To'] = toEmail

        # Create the body of the message (a plain-text and an HTML version).
        html = """\
        <html>
        <head></head>
        <body>
            <h4> %s Links You May Find Interesting Today: </h4>
                %s       
        </body>
        </html>
        """ %(len(links), '<br/><br/>'.join(links))

        # Record the MIME types of both parts - text/plain and text/html.
        mime = MIMEText(html, 'html')
            
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(mime)

        try:
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(fromEmail, password)
            mail.sendmail(fromEmail, toEmail, msg.as_string())
            mail.quit()
            print('Email sent!')
        
        except Exception as e:
            print('Something went wrong... %s' % e)

        r.flushdb()

s = Scrapper(['Jukebox'])
s = Scraper(['database'])
s.parse()
s.store()
if datetime.datetime.now().hour == 13:
    s.email()