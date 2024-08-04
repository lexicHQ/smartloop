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
        
        print_project = lambda x :tabulate(x, headers=['current', 'id', 'title'])
        
        projects = Projects(profile).get_all()

        console.print(print_project([
            ['[*]' if project is not None and proj['id'] == project['id']else '[ ]', 
             proj['id'],
             proj['title']
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


    @app.command(short_help="get project")
    def get(id: Annotated[str, typer.Option(help="id of the project")]):
       
        try:
            profile = UserProfile.load()
            projects = [
                project for project in Projects(profile).get_all() 
                if project.get('id') == id
            ]

            if len(projects) > 0:
                project_properties = []
                expected_keys = ['id', 'title', 'name', 'config', 'created_at']
                for key, value in projects[0].items():
                    if key in expected_keys:
                        if key == 'config':
                            for key, value in value.items():
                                project_properties.append([key, value])
                        else:    
                            project_properties.append([key, value])

                console.print(tabulate(project_properties, headers=['Name', 'Value']))
            else:
                console.print("[red]No project found[/red]")
        except Exception as ex:
            print(ex)

    @app.command(short_help="Set project properties")
    def set(id: Annotated[str, typer.Option(help="project Id to use")], temp: Annotated[float, typer.Option(help="Set a temparature between 0.0 and 1.0")] = 0.3):
        profile = UserProfile.load()
        projects = [
            project for project in Projects(profile).get_all() 
            if project.get('id') == id
        ]
        # check for length
        if len(projects) > 0:
            profile['project'] = projects[0]
            Projects(profile).set_config(dict(temparature=temp))
        else:
            console.print("No project found")

    @app.command(short_help="Delete a project")
    def delete(id: Annotated[str, typer.Option(help="project Id to use")]):
        profile = UserProfile.load()
        projects = [
            project for project in Projects(profile).get_all() 
            if project.get('id') == id
        ]
        # check for length
        if len(projects) > 0:
            profile['project'] = projects[0]
            Projects(profile).delete()
            console.print("Project deleted successfully")
        else:
            console.print("No project found")
