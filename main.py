import sys
import requests
import os
import typer
import uuid
import getpass
import yaml
import time

from rich.progress import Progress, SpinnerColumn

documentum_endpoint='http://localhost:8888/v1/'
bot_id = '663c12de5d317e73090ba573'

app = typer.Typer()

@app.command()
def login():
	username = input('username: ')
	password = getpass.getpass('password: ')

	url = os.path.join(documentum_endpoint, 'users')
	resp = requests.post(url, json=dict(name='', username=username, email=username,password=password, notify=True))
	resp.raise_for_status()
	data = resp.json()

	with open('user.yaml', 'w+') as outfile:
		yaml.dump(data, outfile, default_flow_style=False)
	
	typer.echo("login successful")

@app.command()
def start():
	user_input = input('Enter message (Ctrl-C to exit): ')
	url = os.path.join(documentum_endpoint, 'messages', bot_id)

	with open('user.yaml', 'r') as infile:
		user = yaml.safe_load(infile)

	token = user.get('token')
	uid = str(uuid.uuid4())
	
	resp = requests.post(url, 
					  json=dict(uid=uid,
						text=user_input,
						type='text'
					),headers={
						'Authorization': f"Bearer {token}"
					})
	resp.raise_for_status()

	result = resp.json()
	data = result.get('data', {})
	uid = data.get('uid')

	with Progress(SpinnerColumn()) as progress:
		progress.add_task("thinking...")
		progress.start()
		# observe for responses
		while True:
			try:
				url = os.path.join(documentum_endpoint, 'messages', bot_id, 'recent')
				resp = requests.get(url,headers={
							'Authorization': f"Bearer {token}"
						})
				resp.raise_for_status()
				result = resp.json()
				data = result.get('data', [])

				found = False

				for i in range(len(data)):
					msg = data[i]
					direction = msg['direction']
					payload = msg['payload']
					_uid = payload['uid']
				
					if direction == 'out' and _uid == uid:
						progress.stop()
						for char in payload['text']:
							print(char, end='')
							sys.stdout.flush()
							time.sleep(.01)
						typer.echo('\n')
						found = True
				if found:
					break
			except Exception as ex:
				typer.echo(ex)

			time.sleep(1)	
		
		start()

if __name__ == "__main__":
	app()