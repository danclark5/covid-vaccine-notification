import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

secure_file = '/home/dan/covid_secure.txt'
recipients = [
        ]

with open(secure_file) as f:
    content = f.readlines()
    sender_address = content[0].strip('\n')
    pw = content[1].strip('\n')
    for line in content[2:]:
        recipients.append(line.strip('\n'))

message = MIMEMultipart()
message['From'] = sender_address
message['To'] = ', '.join(recipients)
message['Subject'] = 'COVID-19 Vaccines are available'   #The subject line


def send_message(cvs_available):
    message_text = "Vaccines are available in " + ', '.join(cvs_available)
    message.attach(MIMEText(message_text, 'plain'))
    message_string = message.as_string()

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, pw)
    session.sendmail(sender_address, recipients, message_string)
    session.quit()
cvs_url = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.NJ.json?vaccineinfo"
cvs_headers = {'Referer': 'https://www.cvs.com/immunizations/covid-19-vaccine'}

cvs_response = requests.get(cvs_url, headers = cvs_headers)
cvs_data = json.loads(cvs_response.text)
cvs_available = []

for record in cvs_data['responsePayloadData']['data']['NJ']:
    if record['pctAvailable'] != '0.00%' or record['status'] != 'Fully Booked' or record['totalAvailable'] != '0':
        cvs_available.append(record['city'])

print(cvs_available)

if(cvs_available):
    send_message(cvs_available)



