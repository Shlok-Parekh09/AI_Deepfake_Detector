import os
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'shlok-profile'

def token():
    p = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True)
    values = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
    return values['password']

def api(path, tok, method='GET', body=None):
    req = urllib.request.Request('https://api.github.com/' + path, headers={'User-Agent': 'Shlok-profile-setup', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok}, method=method, data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read()
        return json.loads(raw) if raw else None

if __name__ == '__main__':
    import sys
    tok = token()
    me = api('user', tok)
    if me['login'].lower() != 'shlok-parekh09':
        raise SystemExit('Authenticated GitHub account does not match the intended profile.')
    print('Authenticated account:', me['login'])
    if sys.argv[1] == 'render':
        env = dict(os.environ, GITHUB_TOKEN=tok, PYTHONPATH=str(BASE / 'profile-runtime'))
        commands = [('banners', '../assets'), ('vitals', '../assets/vitals.svg'), ('dossier', '../assets/dossier.svg'), ('skyline', '../assets/skyline.svg'), ('galaxy', '../assets/galaxy.svg'), ('neural', '../assets/neural.svg'), ('ops', '../assets/ops.svg'), ('explorer', '../README.md')]
        for script, out in commands:
            subprocess.run([sys.executable, script + '.py', 'Shlok-Parekh09', out], cwd=ROOT / 'scripts', env=env, check=True)
    elif sys.argv[1] == 'create':
        path = 'repos/Shlok-Parekh09/Shlok-Parekh09'
        try:
            repo = api(path, tok)
            print('Profile repository already exists; will not overwrite it.')
            raise SystemExit(1)
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        repo = api('user/repos', tok, 'POST', {'name': 'Shlok-Parekh09', 'description': 'Shlok Parekh | Agentic AI & Cybersecurity | Animated GitHub profile', 'private': False, 'has_issues': True, 'auto_init': False})
        print('Created:', repo['html_url'])
        import base64
        from nacl.public import PublicKey, SealedBox
        key = api(path + '/actions/secrets/public-key', tok)
        flag = 'SHLOK{ag3nts_d3f3nd_th3_g4l4xy}'
        sealed = SealedBox(PublicKey(base64.b64decode(key['key']))).encrypt(flag.encode())
        api(path + '/actions/secrets/CTF_FLAG', tok, 'PUT', {'encrypted_value': base64.b64encode(sealed).decode(), 'key_id': key['key_id']})
        print('Configured the encrypted CTF secret.')
    elif sys.argv[1] == 'verify':
        path = 'repos/Shlok-Parekh09/Shlok-Parekh09'
        repo = api(path, tok)
        print('Published:', repo['html_url'], 'branch:', repo['default_branch'])
        data = api(path + '/actions/runs?per_page=5', tok)
        for run in data['workflow_runs']:
            print(run['name'], run['status'], run['conclusion'], run['html_url'])
