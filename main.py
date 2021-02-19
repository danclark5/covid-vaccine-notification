import requests
import json
import re
import smtplib
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

def send_message(cfg, msg, cvs_available, shoprite_available):
    msg_text = ""
    if cvs_available:
        msg_text += f"Vaccines are available in CVS locations: {', '.join(cvs_available)}\n\n"
    if shoprite_available:
        shoprite_url = "https://reportsonline.queue-it.net/?c=reportsonline&e=shoprite&t_program=Immunizations"
        msg_text += f"Vaccines are available at Shoprite. Check {shoprite_url} for more information."


    msg.attach(MIMEText(msg_text, 'plain'))
    msg_string = msg.as_string()

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(cfg['sender_address'], cfg['pw'])
    session.sendmail(cfg['sender_address'],cfg['recipients'], msg_string)
    session.quit()

def scrap_cvs():
    cvs_url = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.NJ.json?vaccineinfo"
    cvs_headers = {'Referer': 'https://www.cvs.com/immunizations/covid-19-vaccine'}

    cvs_response = requests.get(cvs_url, headers = cvs_headers)
    cvs_data = json.loads(cvs_response.text)
    cvs_available = []

    for record in cvs_data['responsePayloadData']['data']['NJ']:
        if record['pctAvailable'] != '0.00%' or record['status'] != 'Fully Booked' or record['totalAvailable'] != '0':
            cvs_available.append(record['city'])
    return cvs_available

def scrap_shoprite():
    shoprite_url = "https://reportsonline.queue-it.net/?c=reportsonline&e=shoprite&t_program=Immunizations"
    shoprite_response = requests.get(shoprite_url)
    return not(bool(re.search("There are currently no COVID-19 vaccine appointments available.", shoprite_response.text)))

if __name__ == "__main__":
    cfg = get_configs()
    msg = create_message(cfg)
    shoprite_available = scrap_shoprite()
    cvs_available = scrap_cvs()
    print(f"CVS Availaibility: {cvs_available}, Shoprite Availability: {shoprite_available}")
    
    if(cvs_available or shoprite_available):
        send_message(cfg, msg, cvs_available, shoprite_available)
