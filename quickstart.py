from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    user_id = 'me'
    get_rocket_reach_ids(service, user_id)


def get_rocket_reach_ids(service, user_id):
    mail = set()

    try:
        mail = service.users().messages().list(userId=user_id).execute()
    except Exception as error:
        print('An error occurred: %s' % error)

    id_file = open("rocketreach_id", "w")

    for message in dict(mail).get("messages"):
        try:
            metadata = service.users().messages().get(userId=user_id, id=message.get("id"), format='metadata').execute()
            if str(metadata.get("snippet")).startswith("RocketReach.co"):
                id_file.write(metadata.get("id"))
                print("True")
        except Exception as error:
            print('An error occurred: %s' % error)

    id_file.close()

    activate_rocketreach_accounts(service, user_id)


def activate_rocketreach_accounts(service, user_id):
    id_file = open("rocketreach_id", "r")
    confirm_link_file = open("confirm_links", "a")

    msg_id = id_file.readline()

    while len(msg_id) > 0:
        try:
            message = service.users().messages().get(userId=user_id, id=msg_id,
                                                     format='raw').execute()
            msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
            mime_msg = str(email.message_from_string(msg_str))

            prefix = "ccount belongs to you. Please click:"
            mime_msg = mime_msg[mime_msg.find(prefix) + len(prefix)+1:]
            mime_msg = mime_msg[:mime_msg.find("If you did not")]

            i = 0
            while i < len(mime_msg)-1:
                if mime_msg[i] == "\n":
                    mime_msg = mime_msg[0:i-1] + mime_msg[i+1:]
                i += 1

            print(mime_msg)
            # confirm_link_file.write(mime_msg)
        except Exception as error:
            print('An error occurred: %s' % error)

        msg_id = id_file.readline()

    id_file.close()
    confirm_link_file.close()


if __name__ == '__main__':
    main()



