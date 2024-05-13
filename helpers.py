import requests
from datetime import datetime, timedelta

launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch"
launch_upcoming_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"

# start_time = datetime(1969, 4, 26)
# end_time = datetime(1970, 4, 1)



def all_launches():
    res = requests.get(
        launch_base_url,
        params={
            'launch' : '/2.2.0/launch/',
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
            'ordering' : 'net'
        }
        launches.append(launch_info)
    return launches



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
            'name': launch['name'],
            'last_updated' : launch['last_updated'],
            'launch_date': launch['net'],
            'image_url': launch['image'],
            'status' : launch['status']['name']
        }
        rocket_info = {
            'rocket_name' : launch['rocket']['configuration']['name'],
            'rocket_variant' : launch['rocket']['configuration']['variant']
        }
        mission_info = {
            'mission_name' : launch['mission']['name'],
            'mission_description' : launch['mission']['description'],
            'mission_type' : launch['mission']['type'],
            'mission_orbit' : launch['mission']['orbit']['name']
        }
        pad_info = {
            'pad_name' : launch['pad']['name'],
            'pad_wiki_url' : launch['pad']['wiki_url'],
            'pad_map_url' : launch['pad']['map_url'],
            'pad_location_name' : launch['pad']['location']['name'],
            'pad_map_img' : launch['pad']['map_image'],
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
