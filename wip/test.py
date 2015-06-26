import os.path as osp
import yaml
import requests

class BioProjProject(object):
    url = 'https://bioproj.extra.cea.fr/redmine'

    def __init__(self, project_id, api_key):
        self.api_key = api_key
        self.project_id = project_id
        
    def get(self, path, **kwargs):
        params = {'key': self.api_key}
        params.update(kwargs)
        response = requests.request(url='%s/%s.json' % (self.url, path),
                                    params=params, method='get')
        response.raise_for_status()
        return response.json
        
    def pget(self, path, **kwargs):
        return self.get('projects/%s/%s' % (self.project_id, path), **kwargs)

    def members(self):
        result = []
        for user in self.pget('memberships')['memberships']:
            id = user['user']['id']
            result.append(self.get('users/%s' % id, include='user')['user'])
        return result
        
class TrelloBoard(object):
    url = 'https://api.trello.com/1'

    def __init__(self, board_id, api_key, token):
        self.api_key = api_key
        self.token = token
        self.board_id = board_id
        
    def get(self, path, **kwargs):
        params={'key': self.api_key,
                'token': self.token}
        params.update(kwargs)
        response = requests.request(url='%s/%s' % (self.url, path),
                                    method='get',
                                    params=params)
        response.raise_for_status()
        return response.json
        
    def pget(self, path, **kwargs):
        return self.get('boards/%s/%s' % (self.board_id, path), **kwargs)

    def members(self):
        return self.pget('members')

def open_bioproj_and_trello(config_file=None):
    if config_file is None:
        config_file = osp.expanduser('~/.config/bioproj-trello.yml')
    config = yaml.load(open(config_file))
    bioproj = BioProjProject(**config['bioproj'])
    trello = TrelloBoard(**config['trello'])
    return (bioproj, trello)

if __name__ == '__main__':
    from pprint import pprint
    
    bioproj, trello = open_bioproj_and_trello()
    
    pprint(bioproj.members())

    pprint(trello.members())