import requests
import os

from constants import endpoint
from utils import UserProfile

class Projects:
    def __init__(self, profile: dict):
        self.profile = profile

    def get_all(self):
        url = os.path.join(endpoint, 'users')

        resp = requests.get(url, headers={'x-api-key': self.profile.get('token')})
        resp.raise_for_status()
        result = resp.json()

        data = result['data']
        projects = data['projects']

        return projects