import os
import random

import requests
from dotenv import load_dotenv

COMIC_URL = 'https://xkcd.com/{0}/info.0.json'
VK_API_URL = 'https://api.vk.com/method/{0}'
VK_API_VER = 5.131
MIN_COMIC_NUMBER = 1
MAX_COMIC_NUMBER = 2700
IMAGE_DIR = 'images'


def download_random_comic():
    comic_number = random.randint(MIN_COMIC_NUMBER, MAX_COMIC_NUMBER)
    response = requests.get(COMIC_URL.format(comic_number))
    response.raise_for_status()
    comic_page_information = response.json()
    comic_image_url = comic_page_information['img']
    comic_commentary = comic_page_information['alt']
    response = requests.get(comic_image_url)
    response.raise_for_status()
    os.makedirs(IMAGE_DIR, exist_ok=True)
    with open(os.path.join(IMAGE_DIR, f'{comic_number}.png'), 'wb') as file:
        file.write(response.content)
    return comic_number, comic_commentary


def get_photo_upload_address(access_token, group_id):
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': VK_API_VER,
    }
    method = 'photos.getWallUploadServer'
    params['group_id'] = group_id
    response = requests.get(VK_API_URL.format(method), params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def upload_photo_to_server(upload_url, params, image, directory=IMAGE_DIR):
    with open(os.path.join(directory, image), 'rb') as photo:
        response = requests.post(
            upload_url,
            params,
            files={
                'photo': photo
            }
        )
    response.raise_for_status()
    photo_upload_parameters = response.json()
    processed_photo = photo_upload_parameters['photo']
    server = photo_upload_parameters['server']
    photo_hash = photo_upload_parameters['hash']
    return processed_photo, server, photo_hash


def save_photo(group_id, access_token, photo, server, photo_hash):
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'server': server,
        'hash': photo_hash,
        'v': VK_API_VER,
    }
    response = requests.post(VK_API_URL.format('photos.saveWallPhoto'), params)
    response.raise_for_status()
    saved_photo = response.json()['response'][0]
    owner_id = saved_photo['owner_id']
    media_id = saved_photo['id']
    return owner_id, media_id


def post_photo(access_token, group_id, owner_id, media_id, message):
    params = {
        'access_token': access_token,
        'owner_id': f'-{group_id}',
        'message': message,
        'from_group': 1,
        'attachments': f'photo{owner_id}_{media_id}',
        'v': VK_API_VER,
    }
    response = requests.post(
        VK_API_URL.format('wall.post'),
        params
    )
    response.raise_for_status()


def main():
    load_dotenv('tokens.env')
    access_token = os.environ['VK_ACCESS_TOKEN']
    group_id = os.environ['VK_GROUP_ID']
    comic_number, commentary = download_random_comic()
    try:
        upload_address = get_photo_upload_address(access_token, group_id)
        processed_photo, server, photo_hash = upload_photo_to_server(
            upload_address,
            access_token,
            f'{comic_number}.png'
        )
        owner_id, media_id = save_photo(
            group_id,
            access_token,
            processed_photo,
            server,
            photo_hash
        )
        post_photo(access_token, group_id, owner_id, media_id, commentary)
    finally:
        os.remove(os.path.join(IMAGE_DIR, 'f{comic_number}.png'))


if __name__ == '__main__':
    main()
