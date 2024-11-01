from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import json

from .api import ContactAPI

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]
# https://developers.google.com/people/api/rest/v1/people/get?hl=en#query-parameters
GOOGLE_PERSON_FIELDS = [
    'addresses',
    'ageRanges',
    'biographies',
    'birthdays',
    'calendarUrls',
    #'clientData',
    'coverPhotos',
    'emailAddresses',
    #'events',
    #'externalIds',
    #'genders',
    'imClients',
    #'interests',
    #'locales',
    'locations',
    'memberships',
    #'metadata',
    #'miscKeywords',
    'names',
    'nicknames',
    #'occupations',
    'organizations',
    'phoneNumbers',
    'photos',
    'relations',
    'sipAddresses',
    'skills',
    'urls',
    'userDefined',
]


class GoogleContactAPI(ContactAPI):
    def __init__(self, credentials, scopes=None, token=None):
        super().__init__()
        self.credentials = credentials
        self.token = token
        if scopes:
            self.scopes = scopes
        else:
            self.scopes = SCOPES

    def get_service(self):
        new_token, service = self.get_google_service()
        if new_token and service is None:
            self.token = new_token
            none_token, service = self.get_google_service()

        if service is not None:
            self.service = service
        return self.service

    def get_google_service(self):
        creds = None
        if self.token:
            creds = Credentials.from_authorized_user_info(self.token, scopes=self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    self.credentials, self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run

            json_dict = json.loads(creds.to_json())
            return json_dict, None

        service = build("people", "v1", credentials=creds)
        return None, service

    def _get_contacts(self, page_size=10):
        connections_list = []
        next_page_token = ''
        person_fields = ",".join(GOOGLE_PERSON_FIELDS)
        try:
            while True:
                if not (next_page_token is None):
                    # Call the People API
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=page_size,  # 1000
                        personFields=person_fields,
                        pageToken=next_page_token
                    ).execute()
                    connections_list = connections_list + results.get('connections', [])
                    next_page_token = results.get('nextPageToken')
                else:
                    break
            return connections_list
        except HttpError as err:
            print(err)

    def get_ten_contacts(self):
        try:
            print("List 10 connection names")
            person_fields = ",".join(GOOGLE_PERSON_FIELDS)
            print("personFields", person_fields)
            results = self.service.people().connections().list(
                resourceName="people/me",
                pageSize=100,
                # personFields="names,emailAddresses",
                personFields=person_fields,
            ).execute()

            connections = results.get("connections", [])
            for person in connections:
                names = person.get("names", [])
                if names:
                    name = names[0].get("displayName")
                    print(name)
            return connections

        except HttpError as err:
            print(err)

    def get_all_contacts(self) -> list:
        return self._get_contacts(page_size=1000)

