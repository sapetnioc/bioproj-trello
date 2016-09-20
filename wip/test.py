import os.path as osp
import yaml
import requests

class BioProjProject(object):
    url = 'https://bioproj.extra.cea.fr/redmine'

    def __init__(self, project_id, api_key):
        self.api_key = api_key
        self.project_id = project_id
        
    def _request(self, method, path, headers=None, data=None, **kwargs):
        method_kwargs = {}
        if headers:
            method_kwargs['headers'] = headers
        if data is not None:
            method_kwargs['data'] = data
        params = {'key': self.api_key}
        params.update(kwargs)
        method_kwargs['params'] = params
        url = url='%s/%s.json' % (self.url, path)
        print '!', url, params
        response = method(url=url,
                          **method_kwargs)
        response.raise_for_status()
        return response.json()
    
    def get(self, path, **kwargs):
        return self._request(requests.get, path, **kwargs)
        
    def pget(self, path, **kwargs):
        return self.get('projects/%s/%s' % (self.project_id, path), **kwargs)
    
    def put(self, path, data, **kwargs):
        return self._request(requests.put, path, data=data, header={'content-type': 'application/json; charset=utf-8'}, **kwargs)
        
    def pput(self, path, data, **kwargs):
        return self.put('projects/%s/%s' % (self.project_id, path), data=data, **kwargs)

    def post(self, path, data, **kwargs):
        return self._request(requests.put, path, data=data, header={'content-type': 'application/json; charset=utf-8'}, **kwargs)
        
    def ppost(self, path, data, **kwargs):
        return self.post('projects/%s/%s' % (self.project_id, path), data=data, **kwargs)

    def members(self):
        result = []
        total_count = None
        while total_count is None or len(result) < total_count:
            page = self.pget('memberships', limit=100, offset=len(result))
            if total_count is None:
                total_count = int(page['total_count'])
            for user in page['memberships']:
                id = user['user']['id']
                result.append(self.get('users/%s' % id, include='user')['user'])
        return result
    
    def issues(self):
        return self.get('issues', project_id=self.project_id, include='issues')['issues']

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
        response = requests.get(url='%s/%s' % (self.url, path),
                                params=params)
        response.raise_for_status()
        return response.json()
        
    def pget(self, path, **kwargs):
        return self.get('boards/%s/%s' % (self.board_id, path), **kwargs)

    def members(self):
        return self.pget('members')
        
    def cards(self, filter='all'):
        return trello.pget('cards/%s' % filter)
    
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
    
    #pprint(bioproj.members())
    #pprint(trello.members())
    