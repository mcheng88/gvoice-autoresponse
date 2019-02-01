from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import manipulateMail
from manipulateMail import listMessagesMatchingQuery
from manipulateMail import cleanToEmail
from manipulateMail import SendMessage
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    user_id = 'me'
    label_id_one = 'INBOX'
    label_id_two = 'UNREAD'
    query = "New text message from"
    msg_list = listMessagesMatchingQuery(service, user_id, label_id_one, label_id_two, query)
    print("Total unread messages matching query in inbox: ", str(len(msg_list)))

    cleanedEmailList = cleanToEmail(service, msg_list, user_id)
    messageHtml = "Hi<br/>Html Email<br/>New Lines"
    messagePlain = "Hi\nPlain Email\nNew Lines"
    for email in cleanedEmailList:
        SendMessage(service, messageHtml, messagePlain, email)

if __name__ == '__main__':
    main()
