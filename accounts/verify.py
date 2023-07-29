# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

os.environ['TWILIO_ACCOUNT_SID'] = 'AC8d6bf7858b941a13a075c4af3116f222'
os.environ['TWILIO_AUTH_TOKEN'] = '8c780297dbe2f6e7447634551eb525f7'
os.environ['TWILIO_VERIFY_SERVICE_SID'] = 'VA3169ecddba392f5282f1d91f8b14166b'

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
verify = client.verify.v2.services(os.environ['TWILIO_VERIFY_SERVICE_SID'])

def send(phone):
    verification = verify.verifications.create(to=phone,channel='sms')
    return verification

def check(phone, code):
    try:
        result = verify.verification_checks.create(to=phone, code=code)
    except TwilioRestException:
        print('no')
        return False
    return result.status == 'approved'