import glob
import http
import sys
from typing import Annotated
import requests
import json
import os
import typer
import uuid
import getpass
import yaml
import time
import hashlib
import posixpath
import mimetypes

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.console import Console
from signal import signal, SIGINT
from art import text2art
from pathlib import Path

from constants import endpoint, homedir

from apps import Project
from utils import UserProfile

from services import Projects

console = Console()
app = typer.Typer()

app.add_typer(Project.app, name='project' , short_help= "Manage projects")

def signal_handler (signal_received, frame):
    # Handle any cleanup here
	console.print(f"\n[blue]Bye![/blue]\n")
	exit(0)

def select_project() -> dict:
	profile = UserProfile.load()
	projects = Projects(profile).get_all()
	# must have a project created earlier
	if len(projects) > 0:
		return Project.use()
	
	raise "No project has been created"

@app.command(short_help="Login using a token from https://api.smartloop.ai/v1/redoc")
def login():
	Art = text2art('smartloop.', font='small')
	
	console.print(Art)
	console.print('You can generatate your token from /users/token endpoint')

	token  = getpass.getpass('Enter your token (Token will be invisitble): ')

	UserProfile.save(dict(token=token))

	try:
		Projects(UserProfile.load()).get_all()
		console.print('[green]Successfuly logged in[/green]')
		console.print('Next up explore [cyan]project[/cyan] or use [cyan]run[/cyan] to chat with a document')
	except:
		console.print('[red]Invalid login[/red]')

def chat_to_project(project_id: str):
	user_input = input('Enter message (Ctrl-C to exit): ')
	url = posixpath.join(endpoint, project_id, 'messages')

	profile =  UserProfile.load()
	token = profile.get('token')

	uid = str(uuid.uuid4())
	
	resp = requests.post(url, 
					  json=dict(uid=uid,
						text=user_input,
						type='text'
					),headers={
						'x-api-key': token
					})
	resp.raise_for_status()

	result = resp.json()
	data = result.get('data', {})
	uid = data.get('uid')
	
	timeout = 5*60 + time.time()

	with Progress(SpinnerColumn()) as progress:
		progress.add_task("thinking...")
		progress.start()
		# observe for responses
		while True:
			try:
				url = posixpath.join(endpoint, project_id, 'messages', 'recent')
				
				resp = requests.get(url,headers={'x-api-key': token})
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
				if found or time.time() > timeout:
					break
				time.sleep(1)
			except Exception as ex:
				typer.echo(ex)


@app.command(short_help="Starts a chat session with a selected project")
def run():
	try:
		profile = UserProfile.load()
		# check if logged in
		if 'token' in profile.keys():
			if 'project' in profile.keys():
				project =  profile['project']

				console.print(f"[green]Current project: [underline]{project.get('title')}({project['name']})[/green][/underline]")
				# chat till the cancelled
				while True:
					chat_to_project(project['id'])
					time.sleep(1)
			else:
				select_project()
				run()
		else:
			login()
	except Exception as ex:
		console.print(ex)


@app.command(short_help="Upload documents for a slected project")
def upload(path: Annotated[str, typer.Option(help="folder or file path")]):
	profile = UserProfile.load()
	project = profile.get('project', None)
	
	# check if a project is selected
	if project is None:
		project = select_project()

	path = os.path.expanduser(path)
	
	console.print(f"[green]Upload to project: [underline]{project.get('title')}({project.get('name')})[/green][/underline]")

	url = posixpath.join(endpoint, f"{project['id']}/documents")

	files = []

	if os.path.isdir(path):
		files = glob.glob(os.path.join(path, '*.pdf'))
		# extend file types
		files.extend(glob.glob(os.path.join(path, '*.docx')))
		files.extend(glob.glob(os.path.join(path, '*.txt')))
	else:
		files.append(path)

	for file in files:
		console.print(f"Uploading {file}")
		with Progress(SpinnerColumn()) as progress:
			task = progress.add_task("uploading...")
			progress.start()
			try:
				with open(file, 'rb') as infile:
					mimetype = mimetypes.guess_type(file)
					resp = requests.put(url, headers={
						'x-api-key': profile['token']
					}, 
					files={
						'file': (Path(infile.name).name, infile.read(), mimetype[0])
					})
					
					# handled error
					if resp.status_code == http.HTTPStatus.BAD_REQUEST:
						progress.stop()
						console.print(f"[red]{resp.json()['detail']}[/red]")
						return

					resp.raise_for_status()

					data = resp.json()
					progress.console.print("Uploaded.")
					progress.console.print("Processing document...")
					while True:
						if 'id' in data:
							# wait for document to be processed
							url = posixpath.join(endpoint, project.get('id'), 'documents', data['id'])
							resp =requests.get(url, headers={
								'x-api-key': profile['token']
							})
							resp.raise_for_status()
							_data = resp.json()
							document = _data.get('data', None)
							# check if not pending 
							if document is None or not document.get('pending', False):
								break
						else:
							break
					progress.stop()
					console.print("Completed.")
			except Exception as ex:
				console.print(f"[red]{ex}[/red]")


@app.command(short_help="Find out which account you are logged in")
def whoami():
	try:
		profile = UserProfile.load()
		token = profile.get('token')

		url = posixpath.join(endpoint, 'users')
		
		resp = requests.get(url, headers={
			'x-api-key': token
		})
		resp.raise_for_status()
		resp = resp.json()
		# check for data
		if 'data' in resp:
			data = resp['data']
			console.print(f"{data.get('name')}")
	except Exception as ex:
		console.print(f"[red]{ex}[/red]")

def bootstrap():
	signal(SIGINT, signal_handler)

	if not os.path.isdir(homedir):
		os.makedirs(homedir)
	
	app()

if __name__ == "__main__":	
	bootstrap()