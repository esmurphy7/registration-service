import argparse
import pickle
import os.path
from __future__ import print_function
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import pubsub_v1

def register_feed(classroom_service, body):
    try:
        registration = classroom_service.registration().create(body=body).execute()
    except errors.HttpError as error:
        print('Failed to register feed.')
        return error
    return registration

def register_course_feed(project_id, topic_name, classroom_service, course_id):
    body = {
        "feed": {
            "feedType": "COURSE_WORK_CHANGES",
            "courseWorkChangesInfo": {
                "courseId": f"{course_id}"
            }
        },
        "cloudPubsubTopic": {
            "topicName": f"projects/{project_id}/topics/{topic_name}"
        }
    }

    registration = register_feed(classroom_service=classroom_service, body=body)
    return registration


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Google Cloud project ID")
    parser.add_argument("topic_name", help="Pub/Sub topic name")
    
    subparsers = parser.add_subparsers(dest="command")

    course_parser = subparsers.add_parser("course", help=register_course_feed.__doc__)

    args = parser.parse_args()

    SCOPES = [
        'https://www.googleapis.com/auth/classroom.push-notifications',
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/pubsub'
    ]
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    classroom_service = build('classroom', 'v1', credentials=creds)

    if args.command == "course":
        register_course_feed(args.project_id, args.topic_name, classroom_service, course_id)