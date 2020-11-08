from __future__ import print_function
import argparse
import pickle
import os.path
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import pubsub_v1
from google.oauth2 import service_account

def register_feed(classroom_service, body):
    try:
        registration = classroom_service.registrations().create(body=body).execute()
    except errors.HttpError as error:
        print('Failed to register feed.')
        return error
    return registration

def register_course_feed(project_id, topic_name, classroom_service, course_id):
    body = {
        "feed": {
            "feedType": "COURSE_WORK_CHANGES",
            "courseWorkChangesInfo": {
                "courseId": "{}".format(course_id)
            }
        },
        "cloudPubsubTopic": {
            "topicName": "projects/{}/topics/{}".format(project_id, topic_name)
        }
    }

    registration = register_feed(classroom_service=classroom_service, body=body)
    return registration


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", type=str, help="Google Cloud project ID")
    parser.add_argument("topic_name", type=str, help="Pub/Sub topic name")    
    parser.add_argument("course_id", help=register_course_feed.__doc__)
    
    args = parser.parse_args()

    # test that this app can send requests authenticated as the service account by 
    # 1. authenticating with the downloaded private key json file (via the GOOGLE_APPLICATION_CREDENTIALS env variable)
    # 2. querying pubsub data in our project (getting the elph topic path)
    # publisher = pubsub_v1.PublisherClient()
    # topic_path = publisher.topic_path(args.project_id, args.topic_name)
    # print("topic_path: {}".format(topic_path))

    # test that this app has permission to query a user's data by 
    # 1. using the user's access token
    # 2. querying the user's data
    SCOPES = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.push-notifications',
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/pubsub'
    ]
    SERVICE_ACCOUNT_FILE = './pubsub-system.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    classroom_service = build('classroom', 'v1', credentials=credentials)
    # course = classroom_service.courses().get(id=args.course_id).execute()
    # print("course.id: {}".format(course.id))

    register_course_feed(args.project_id, args.topic_name, classroom_service, args.course_id)