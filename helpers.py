import requests
from datetime import datetime, timedelta
from models import Launch

launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch"
launch_upcoming_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"


def all_launches(url=None):
    if url is None:
        url = launch_base_url
    res = requests.get(
        url,
        params={
            'ordering' : 'net'
        }
    )
    data = res.json()

    launches = []
    for launch in data['results']:
        launch_info = {
            'id' : launch['id'],
            'date' : launch['net'],
            'name' : launch['name'],
            'status' : launch['status']['name'],
            'description' : launch['mission']['description'],
            'img_url' : launch['image'],
            'organization' : launch['launch_service_provider']['name'],
            'organization_type' : launch['launch_service_provider']['type'],
            'location' : launch['pad']['location']['name']
        }
        launches.append(launch_info)
    
    pagination = {
        'count' : data['count'],
        'next' : data['next'],
        'previous' : data['previous']
    }
    return launches, pagination



def get_launch(launch_name):
    res = requests.get(
        launch_base_url,
        params={
            'launch' : '/2.2.0/launch/',
            'mode' : 'normal',
            'name' : launch_name
        }
    )
    data = res.json()
    launch_data = []
    for launch in data['results']:
        launch_info = {
            'Name': launch['name'],
            'Last_Updated' : launch['last_updated'],
            'Launch_Date': launch['net'],
            'Img_URL': launch['image'],
            'Status' : launch['status']['name']
        }
        rocket_info = {
            'Rocket_Name' : launch['rocket']['configuration']['name'],
            'Rocket_Variant' : launch['rocket']['configuration']['variant']
        }
        mission_info = {
            'Mission_Name' : launch['mission']['name'],
            'Mission_Description' : launch['mission']['description'],
            'Mission_Type' : launch['mission']['type'],
            'Mission_Orbit' : launch['mission']['orbit']['name']
        }
        pad_info = {
            'Pad_Name' : launch['pad']['name'],
            'Pad_Wiki_URL' : launch['pad']['wiki_url'],
            'Pad_Map_URL' : launch['pad']['map_url'],
            'Pad_Location_Name' : launch['pad']['location']['name'],
            'Pad_Map_Img' : launch['pad']['map_image'],
        }
        launch_data.append(launch_info)
        launch_data.append(rocket_info)
        launch_data.append(mission_info)
        launch_data.append(pad_info)

    return launch_data



def previous_launches(start_time, end_time, next_url=None):

    if next_url:
        res = requests.get(next_url)
    else:
        res = requests.get(
            launch_base_url, 
            params={
                'net__get' : start_time.isoformat(), 
                'net__lte' : end_time.isoformat(),
                'mode' : 'detailed',
                'limit': 5,
                'ordering' : 'net'
                }
            )
    data = res.json()
    launches = []
    for launch in data['results']:
        launch_info = {
            'name': launch['name'],
            'date': launch['net'],
            'image_url': launch['launch_service_provider']['image_url']
        }
        launches.append(launch_info)

    next_url = f"next: {data.get('next')}"
    return launches, next_url



def launch_search(url, search_term):
    if url is None:
        url = launch_base_url
    res = requests.get(
        url,
        params={
            'ordering' : 'net',
            'search' : search_term
        }
    )
    data = res.json()

    if data['count'] == 0:
        return None
    else:
        searched_launches = []
        for launch in data['results']:
            launch_info = {
                'id' : launch['id'],
                'date' : launch['net'],
                'name' : launch['name'],
                'status' : launch['status']['name'],
                'description' : launch['mission']['description'],
                'img_url' : launch['image'],
                'organization' : launch['launch_service_provider']['name'],
                'organization_type' : launch['launch_service_provider']['type'],
                'location' : launch['pad']['location']['name']
            }
            searched_launches.append(launch_info)

        pagination = {
            'count' : data['count'],
            'next' : data['next'],
            'previous' : data['previous']
        }   
        return searched_launches, pagination
