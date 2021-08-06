import argparse
import requests
from json import loads
import time
import datetime
from pathlib import Path
from os import getcwd

api_url = 'https://discord.com/api/v9'

def get_username(token, user_id):
    headers = {
        'authorization': token,
    }
    url = f'{api_url}/users/{user_id}'
    resp = requests.get(url, headers=headers)
    json = loads(resp.text)
    
    return json['username'] + '#' + json['discriminator']

def get_args():
    parser = argparse.ArgumentParser(description="Download all stream preview images of a Discord user.")
    
    parser.add_argument("-t", "--token", type=str, help="your Discord token", required=True)
    parser.add_argument("-g", "--guild", type=int, help="the id of the guild (server) the user is on", required=True)
    parser.add_argument("-c", "--channel", type=int, help="the id of the server the user is on", required=True)
    parser.add_argument("-u", "--user", type=int, help="the id of the user", required=True)
    parser.add_argument("-o", "--outputDirectory", type=Path, help="the directory in which the images should be saved")
    
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    
    token = args.token
    
    guild_id = str(args.guild)
    channel_id = str(args.channel)
    user_id = str(args.user)
    
    if args.outputDirectory is None:
        image_directory = getcwd()
    else:
        image_directory = args.outputDirectory

    username = get_username(token, user_id)

    headers = {
        'authorization': token,
    }
    
    image_url = None
    image_count = 0
    while True:
        try:
            link_response = requests.get(f'{api_url}/streams/guild:{guild_id}:{channel_id}:{user_id}/preview', headers=headers)
            #print(link_response.text)
            
            json = loads(link_response.text)
            try:
                new_image_url = json['url']
                
                if image_url == new_image_url:
                    time.sleep(15)
                    continue
                
                timestamp = str(datetime.datetime.now()).replace(' ', 'T').replace(':', '-').replace('.', '-')
                print(f'New Image ({timestamp}) {image_count}:')
                image_url = new_image_url
                print('  ' + image_url)
                
                image_response = requests.get(image_url)
                image = image_response.content
                image_path = f'{image_directory}\\{username}'
                # create user directory if it does not exist
                Path(image_path).mkdir(parents=True, exist_ok=True)
                image_path += f'\\{timestamp}.jpg'
                
                with open(image_path, 'wb', ) as image_file:
                    image_file.write(image)
                print('  ' + image_path)
                image_count += 1
            except KeyError:
                # url retrieving did not work
                print(f'Error retrieving URL: {json["message"]}')
            time.sleep(15)
        except KeyboardInterrupt:
            print('Stopping...')
            exit()