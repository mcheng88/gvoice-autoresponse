from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def readMessagesMatchingQuery(service, user_id, label_id_one, label_id_two, query):
    unread_msgs = service.users().messages().list(userId = user_id, labelIds=[label_id_one, label_id_two], q=query).execute()
    return unread_msgs['messages']


