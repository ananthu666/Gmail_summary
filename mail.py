from __future__ import print_function
import summarize
from summarize import sum
import os.path
from googleapiclient import errors 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)    
    return service


def search_message(service, user_id, search_string):

    try:
        list_ids = []

        search_ids = service.users().messages().list(userId=user_id, q=search_string).execute()
        try:
            ids = search_ids['messages']
        except KeyError:
            print("WARNING: the search queried returned 0 results")
            print("returning an empty string")
            return ""

        if len(ids)>1:
            for msg_id in ids:
                list_ids.append(msg_id['id'])
            return(list_ids)

        else:
            list_ids.append(ids[0]['id'])
            return list_ids
        
    except errors.HttpError as e:
         print(f"An error occurred: {e}")


def get_message(service, user_id, msg_id):
    try:
        
        message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()
        # print("message",message)
        
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        # print(type(msg_str))
        
        mime_msg = email.message_from_bytes(msg_str)
        # print("mime_msg",mime_msg)
        
        content_type = mime_msg.get_content_maintype()
        # print('here')
        if content_type == 'multipart':

            parts = mime_msg.get_payload()

            final_content = parts[0].get_payload()
            return final_content

        elif content_type == 'text':
            return mime_msg.get_payload()

        else:
            return ""
            print("\nMessage is not text or multipart, returned an empty string")
    except Exception:
         print(f"An error occurred")




service1=get_service()
print(service1)
service2=search_message(service1,'me','ananthujayakumar02@gmail.com')
print(service2[0])
service3=get_message(service1,'me',service2[0])
print(service3)
sum(service3)