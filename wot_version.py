import smtplib
from email.mime.text import MIMEText
import os
import sys
import time as time_
import requests
from bs4 import BeautifulSoup
from loguru import logger
from dotenv import load_dotenv
from fake_headers import Headers
import schedule


def send_msg(sending_version: str, sending_href_to_make_sure: str) -> None:
    """Sending email message function

    Args:
        sending_version (str): The first parameter contains new game version to informate
        sending_href_to_make_sure (str): The second parameter contains href
            to third party site to check everything is ok
    """
    msg = MIMEText(
        f'WOT UPDATE {sending_version}\n'
        f'Go and check it out on {sending_href_to_make_sure}\n')
    msg['Subject'] = f'WOT UPDATE {sending_version}'

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(os.getenv('EMAIL_FROM'), os.getenv('P1L_APP_KEY'))
        smtp.sendmail(
            os.getenv('EMAIL_FROM'),
            os.getenv('EMAIL_TO'),
            msg.as_string())
        sys.exit()


@schedule.repeat(schedule.every().hour)
def check_new_version() -> None:
    """Checks the relevance of the current version
    """
    def get_soup(url: str) -> BeautifulSoup:
        """Getting BeautifulSoup object

        Args:
            url (str): The first parameter

        Returns:
            BeautifulSoup: BeautifulSoup object to parse
        """
        request = requests.get(url, timeout=5, headers=Headers().generate())
        return BeautifulSoup(request.text, 'html.parser')

    def get_current_version() -> str:
        """Getting current game version to check is up-to-date

        Returns:
            str: game version to compare to
        """
        soup = get_soup(os.getenv('HOME_SITE'))
        return soup.find('div', id='dle-content').div.find_all('span')[1].text

    version_to_compare = get_current_version()
    href_check_new_version = os.getenv('AWAY_SITE')
    soup = get_soup(href_check_new_version)
    spans = soup.find_all(string=version_to_compare)

    if len(spans) < 24:
        version_to_compare = soup.select("i.icon-shuffle+span")[0].text
        logger.warning("A new version has been released")
        send_msg(version_to_compare, href_check_new_version)
    else:
        logger.info("No update required")


if __name__ == '__main__':
    logger.add('logs\\wot.log',
               format='{time} {level} {message}',
               level='INFO')
    load_dotenv()

    while True:
        schedule.run_pending()
        time_.sleep(1)
