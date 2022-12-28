import os
import random

import requests
from dotenv import load_dotenv

COMIC_URL = 'https://xkcd.com/{0}/info.0.json'
VK_API_URL = 'https://api.vk.com/method/{0}'
VK_API_VER = 5.131
MIN_COMIC_NUMBER = 1
MAX_COMIC_NUMBER = 2700


def download_image_in_folder(url, directory, filename):
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, filename), 'wb') as file:
        file.write(response.content)


def download_random_comic():
    comic_number = random.randint(MIN_COMIC_NUMBER, MAX_COMIC_NUMBER)
    response = requests.get(COMIC_URL.format(comic_number))
    response.raise_for_status()
    comic_page_information = response.json()
    comic_image_url = comic_page_information['img']
    comic_commentary = comic_page_information['alt']
    download_image_in_folder(comic_image_url, 'images', f'{comic_number}.png')
    return comic_number, comic_commentary


def get_photo_upload_address(params, group_id):
    method = 'photos.getWallUploadServer'
    params['group_id'] = group_id
    response = requests.get(VK_API_URL.format(method), params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def upload_photo_to_server(upload_url, params, image, directory='images'):
    with open(os.path.join(directory, image), 'rb') as photo:
        response = requests.post(
            upload_url,
            params,
            files={
                'photo': photo
            }
        )
        response.raise_for_status
        photo_upload_parameters = response.json()
        processed_photo = photo_upload_parameters['photo']
        server = photo_upload_parameters['server']
        hash = photo_upload_parameters['hash']
        return processed_photo, server, hash


def save_photo(group_id, params, photo, server, hash):
    params['group_id'] = group_id
    params['photo'] = photo
    params['server'] = server
    params['hash'] = hash
    response = requests.post(VK_API_URL.format('photos.saveWallPhoto'), params)
    response.raise_for_status()
    saved_photo = response.json()['response'][0]
    owner_id = saved_photo['owner_id']
    media_id = saved_photo['id']
    return owner_id, media_id


def post_photo(params, group_id, owner_id, media_id, message):
    params['owner_id'] = f'-{group_id}'
    params['message'] = message
    params['from_group'] = 1
    params['attachments'] = f'photo{owner_id}_{media_id}'
    response = requests.post(
        VK_API_URL.format('wall.post'),
        params
    )
    response.raise_for_status()
    print(response.json())
    return


def delete_comic(comic_number):
    os.remove(f'images/{comic_number}.png')


def main():
    load_dotenv('tokens.env')
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']
    params = {
        'access_token': vk_access_token,
        'v': VK_API_VER,
    }
    comic_number, commentary = download_random_comic()
    upload_address = get_photo_upload_address(params, vk_group_id)
    processed_photo, server, hash = upload_photo_to_server(
        upload_address,
        params,
        f'{comic_number}.png'
    )
    owner_id, media_id = save_photo(
        vk_group_id,
        params,
        processed_photo,
        server,
        hash
    )
    post_photo(params, vk_group_id, owner_id, media_id, commentary)
    delete_comic(comic_number)


if __name__ == '__main__':
    main()
