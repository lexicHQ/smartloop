from typing import Annotated
import typer
import requests
import posixpath
import os
import re

from tabulate import tabulate

import inquirer
from inquirer.themes import GreenPassion

from smartloop.services import Projects
from smartloop.constants import endpoint
from smartloop.utils import UserProfile

from rich.console import Console

console = Console()

class Project:
    app = typer.Typer()

    @app.command(short_help="Select a project")
    def select() -> dict:
        profile = UserProfile.load()
        projects = Projects(profile).get_all()	
        
        _projects = [f"{proj['title']}({proj['name']})" for proj in projects]
        
        try:
            projects_list = [
                inquirer.List(
                    "project",
                    message="Select a project from the options below",
                    choices=_projects,
                ),
            ]

            answer = inquirer.prompt(projects_list, theme=GreenPassion())
            current_selection =  answer.get('project') if answer is not None else None

            if current_selection is not None:
                name = re.findall('\(([^)]+)\)', current_selection)[0]

                selected = [project for project in projects if project.get('name') == name][0]
                
                profile['project'] = selected
                
                UserProfile.save(profile)

                console.print(f"Default project set to: [underline]{selected['name']}[/underline]")
                
                return selected
        except Exception as ex:
            console.print(ex)

     
    @app.command(short_help="List all projects")
    def list():
        profile = UserProfile.load()
        project = profile.get('project', None)
        
        print_project = lambda x :tabulate(x, headers=['current','id', 'title', 'name', 'temp'])
        
        projects = Projects(profile).get_all()

        console.print(print_project([
            ['[*]' if project is not None and proj['id'] == project['id']else '[ ]', 
             proj['id'], 
             proj['title'], 
             proj['name'],
             proj['config'].get('temparature', 0.3)
            ]
            for proj in projects
        ]))


    @app.command(short_help="Create a new project")
    def create(name: Annotated[str, typer.Option(help="The name of the project")]):
        url = posixpath.join(endpoint, 'projects')
        profile = UserProfile.load()
        try:
            resp = requests.put(url, headers={'x-api-key': profile['token']}, json=dict(title=name))
            resp.raise_for_status()

            print("Project created successfully")
        except Exception as ex:
            print(ex)

    @app.command(short_help="Set the default project")
    def set(id: Annotated[str, typer.Option(help="project Id to use")]):
        profile = UserProfile.load()
        projects = Projects(profile).get_all()
        project = [project for project in projects if project.get('id') == id]

        if len(project) > 0:
            profile['project'] = project[0]
            console.print(f"{project[0]['title']} as set as default project")
            UserProfile.save(profile)
        else:
            console.print("No project found")

    @app.command(short_help="Set temparature")
    def set(temp: Annotated[float, typer.Option(help="Set a temparature between 0.0 and 1.0")]):
        profile = UserProfile.load()
        selected = profile.get('project', None)
        # project is selected
        if selected is not None:
            Projects(profile).set_config(dict(temparature=temp))
        else:
            console.print('[red] No project is selected[/red]')