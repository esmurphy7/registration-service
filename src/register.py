import argparse
import pickle
import os.path
from google.cloud import pubsub_v1
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def register_domain(project_id, topic_name, classroom_service):
    publisher = pubsub_v1.PublisherClient()

    # Call the Classroom API
    results = classroom_service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Google Cloud project ID")
    parser.add_argument("topic_name", help="Pub/Sub topic name")
    
    subparsers = parser.add_subparsers(dest="command")

    domain_parser = subparsers.add_parser("domain", help=register_domain.__doc__)
    domain_parser.add_argument("topic_name")

    args = parser.parse_args()

    SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']
    # SCOPES = ['https://www.googleapis.com/auth/classroom.push-notifications','https://www.googleapis.com/auth/classroom.rosters.readonly']
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

    classroom_service = build('classroom', 'v1', credentials=creds)

    if args.command == "domain":
        register_domain(args.project_id, args.topic_name, classroom_service)