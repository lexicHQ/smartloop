import posixpath
import requests
import os

from smartloop.constants import endpoint

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
    
    def set_config(self, config:dict):
        project_id = self.profile.get('project')['id']
        
        url = posixpath.join(endpoint, project_id, 'config')
        resp = requests.post(url, headers={'x-api-key': self.profile.get('token')}, json=config)
        resp.raise_for_status()
