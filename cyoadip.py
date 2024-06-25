import os
import io
import json
import re
import asyncio
import aiohttp
from PIL import Image

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_json(file_path, json_data, minify):
    with open(file_path, 'w', encoding='utf-8') as f:
        indent = None if minify else 2
        separators = (',', ':') if minify else None
        json.dump(json_data, f, indent=indent, separators=separators)

def find_quality(im, target=50000):
    Qmin, Qmax = 30, 100
    Qacc = -1
    while Qmin <= Qmax:
        m = (Qmin + Qmax) // 2
        buffer = io.BytesIO()
        im.save(buffer, format="WEBP", quality=m)
        s = buffer.getbuffer().nbytes
        if s <= target:
            Qacc = m
            Qmin = m + 1
        else:
            Qmax = m - 1
    if Qacc > -1:
        return Qacc
    else:
        print(f"No acceptable quality below filesize {target} bytes")
        return find_quality(im, target * 2)

async def refresh_url(session, url, TOKEN, semaphore):
    async with semaphore:
        api_url = "https://discord.com/api/v9/attachments/refresh-urls"
        payload = {'attachment_urls': [url]}
        headers = {'Authorization': f'Bot {TOKEN}'}
    
        async with session.post(api_url, json=payload, headers=headers) as response:
            # print(response)
            if response.status == 200:
                refreshed_urls = await response.json()
                # print(refreshed_urls)
                return refreshed_urls['refreshed_urls'][0]['refreshed']
            else:
                print(f"Failed to refresh URL: {url}")
                return None

async def download_image(session, url, semaphore):
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Failed to download image: {url}")
                return None

async def process_image(session, url, index, NEW_PREFIX, IMAGE_PATH, IMAGE_FOLDER, TOKEN, semaphore):
    refreshed_url = await refresh_url(session, url, TOKEN, semaphore)
    if refreshed_url:
        img_data = await download_image(session, refreshed_url, semaphore)
        if img_data:
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            image_name = f'image_{index}.webp'
            image_path = os.path.join(IMAGE_PATH, image_name)
            img.save(image_path, format='WEBP', quality=find_quality(img))
            return f'{NEW_PREFIX}/{IMAGE_FOLDER}/{image_name}'
    return url

async def update_images(json_data, NEW_PREFIX, IMAGE_PATH, IMAGE_FOLDER, TOKEN, RATE_LIMIT):
    urls = list(set(re.findall(r'https://[^?"]*discordapp[^?"]*', json.dumps(json_data))))
    semaphore = asyncio.Semaphore(RATE_LIMIT)
    async with aiohttp.ClientSession() as session:
        tasks = [process_image(session, url, idx, NEW_PREFIX, IMAGE_PATH, IMAGE_FOLDER, TOKEN, semaphore) for idx, url in enumerate(urls)]
        new_urls = await asyncio.gather(*tasks)
    url_map = dict(zip(urls, new_urls))
    return update_urls(json_data, url_map)

def update_urls(json_data, url_map):
    def traverse_and_modify(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["image", "imageLink"] and isinstance(value, str) and value in url_map:
                    data[key] = url_map[value]
                else:
                    traverse_and_modify(value)
        elif isinstance(data, list):
            for item in data:
                traverse_and_modify(item)
    traverse_and_modify(json_data)
    return json_data

async def main():
    # Default values
    directory_path = os.getcwd()
    TOKEN = 'YOUR TOKEN'
    PROJECT_FILE = 'project.json'
    OUTPUT_FILE = 'project_new.json'
    IMAGE_FOLDER = 'images'
    NEW_PREFIX = ''  # Replace with your new prefix
    PROJECT_PATH = os.path.join(directory_path,PROJECT_FILE)
    IMAGE_PATH = os.path.join(directory_path, IMAGE_FOLDER)
    OUTPUT_PATH = os.path.join(directory_path, OUTPUT_FILE)
    MINIFY = False # turn true to minify output json
    RATE_LIMIT = 2
    if(os.path.exists(OUTPUT_PATH)):
        os.remove(OUTPUT_PATH)
    
    os.makedirs(IMAGE_PATH, exist_ok=True)
    
    data = read_json(PROJECT_PATH)
    new_data = await update_images(data, NEW_PREFIX, IMAGE_PATH, IMAGE_FOLDER, TOKEN, RATE_LIMIT)
    write_json(OUTPUT_PATH, new_data, MINIFY)

if __name__ == "__main__":
    asyncio.run(main())
