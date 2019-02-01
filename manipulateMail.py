from __future__ import print_function
import pickle
import os.path
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes

def listMessagesMatchingQuery(service, user_id, label_id_one, label_id_two, query):
    unread_msgs = service.users().messages().list(userId = user_id, labelIds=[label_id_one, label_id_two], q=query).execute()
    return unread_msgs['messages']

# Cleans to a list of emails with the ability to be replied to and marks
# email as read
# An Email will have a Subject, Sender, Message-ID, Referneces, In-Reply-To, Snippet and SMS
def cleanToEmail(service, messageList, user_id):
    smsList = [ ]
    for msg in messageList:
        temp_dict = {  }
        msgid = msg['id']
        temp_dict['gMsg'] = msg
        message = service.users().messages().get(userId = user_id, id=msgid).execute()
        payload = message['payload']
        header = payload['headers']
        for subj in header:
            if subj['name'] == 'Subject':
                msg_subj = subj['value']
                temp_dict['Subject'] = msg_subj
        for sender in header:
            if sender['name'] == 'From':
                msg_from = sender['value']
                temp_dict['From'] = msg_from
        for to in header:
            if to['name'] == 'To':
                temp_dict['To'] = to['value']
        for msgId in header:
            if msgId['name'] == 'Message-ID':
                msg_id = msgId['value']
                temp_dict['Message-ID'] = msg_id
        for ref in header:
            if ref['name'] == 'References':
                reference = ref['value']
                temp_dict['References'] = reference
        for inreply in header:
            if inreply['name'] == 'In-Reply-To':
                inreplyto = inreply['value']
                temp_dict['In-Reply-To'] = inreplyto

        temp_dict['Snippet'] = message['snippet']
        temp_dict['SMS'] = cleanSnippetToMessage(temp_dict['Snippet'])
        print(temp_dict)
        smsList.append(temp_dict)
        service.users().messages().modify(userId=user_id, id=msgid,body={ 'removeLabelIds': ['UNREAD']}).execute()
    return smsList

def cleanSnippetToMessage(snip):
    retStr = snip
    return retStr

def create_message(sender, to, subject, message_id, in_reply_to, references, messageText):
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = "Re: "+subject
    message['message_id'] = message_id
    message['in_reply_to'] = in_reply_to
    message['references'] = references + "\n" + message_id

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def createText(mes):
    pass

def SendMessage(service,  msgHtml, msgPlain, smsDict):
    message1 = CreateMessageHtml( msgHtml, msgPlain, smsDict)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def CreateMessageHtml(msgHtml, msgPlain, smsDict):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Re: ' + smsDict['Subject']
    msg['From'] = smsDict['To']
    msg['To'] = smsDict['From']
    msg['Message-ID'] = smsDict['Message-ID']
    msg['References'] = smsDict['References'] + '\n' + smsDict['Message-ID']
    msg['In-Reply-To'] = smsDict['Message-ID']
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body
