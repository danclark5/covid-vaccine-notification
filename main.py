import requests
import json
import re
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

secure_file = '/home/dan/covid_secure.txt'

def get_configs():
    cfg = {'recipients': []}
    with open(secure_file) as f:
        content = f.readlines()
        cfg['sender_address'] = content[0].strip('\n')
        cfg['pw'] = content[1].strip('\n')
        for line in content[2:]:
            cfg['recipients'].append(line.strip('\n'))
    return cfg

def create_message(cfg):
    msg = MIMEMultipart()
    msg['From'] = cfg['sender_address']
    msg['To'] = ', '.join(cfg['recipients'])
    msg['Subject'] = 'COVID-19 Vaccines are available'
    return msg

def send_message(cfg, msg, cvs_available):
    msg_text = ""
    if cvs_available:
        msg_text += "Vaccines are available in CVS locations:<br/>"
        msg_text += cvs_link_html()
    for site, stats in cvs_available.items():
        msg_text += cvs_site_html(site, stats)


    msg.attach(MIMEText(msg_text, 'html'))
    msg_string = msg.as_string()

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(cfg['sender_address'], cfg['pw'])
    session.sendmail(cfg['sender_address'],cfg['recipients'], msg_string)
    session.quit()

def cvs_site_html(site, stats):
    map_link = f"https://www.google.com/maps/place/{site},+NJ"
    line = f"<a href='{map_link}'>{site}</a>:"
    line += f" status: {stats['status']}<br/>"
    return line

def cvs_link_html():
    link = "<a href='https://www.cvs.com/immunizations/covid-19-vaccine#'>Click here to register</a><br/>"
    return link

def scrape_cvs():
    cvs_url = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.NJ.json?vaccineinfo"
    cvs_headers = {'Referer': 'https://www.cvs.com/immunizations/covid-19-vaccine'}

    cvs_response = requests.get(cvs_url, headers = cvs_headers)
    cvs_data = json.loads(cvs_response.text)
    cvs_available = {}

    for record in cvs_data['responsePayloadData']['data']['NJ']:
        print(record)
        if record['status'] != 'Fully Booked':
            stats = {
                'status': record['status']
                }
            cvs_available[record['city']] = stats
    return cvs_available

def current_date():
    return datetime.datetime.now().strftime('%x %X')

if __name__ == "__main__":
    print (f"Started: {current_date()}")
    cfg = get_configs()
    msg = create_message(cfg)
    cvs_available = scrape_cvs()

    if(cvs_available):
        send_message(cfg, msg, cvs_available)
    else:
        print("None available at CVS")
