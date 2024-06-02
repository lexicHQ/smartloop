import os
import yaml
from constants import homedir

class UserProfile:
    @staticmethod
    def load() -> dict:
        path = os.path.join(homedir, 'user.yaml')
        try:
            if os.path.exists(path):
                with open(path, 'r') as infile:
                    _yaml = yaml.safe_load(infile)
                    return _yaml
        except Exception as ex:
            print(ex)

        return dict()
    
    @staticmethod
    def save(profile:dict):
        with open(os.path.join(homedir, 'user.yaml'), 'w+') as outfile:
            yaml.dump(profile, outfile, default_flow_style=False)