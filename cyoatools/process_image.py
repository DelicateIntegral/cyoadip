import io
import os
import base64
import asyncio
import aiohttp
from PIL import Image

async def base64_to_webp(base64_string, key, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES):
    image_data = base64.b64decode(base64_string.split(",")[1])
    image_name = f'image_{key}.webp'
    image_path = os.path.join(IMAGE_PATH, image_name)
    await save_images(image_data, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES)
    url = f'{IMAGE_FOLDER}/{image_name}'
    return {key: url}

async def download_image(session, url, key, semaphore, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES):
    async with semaphore:
        image_name = f'image_{key}.webp'
        image_path = os.path.join(IMAGE_PATH, image_name)
        if not os.path.exists(image_path) or OVERWRITE_IMAGES:
            print(f"downloading image {key}...")
            async with session.get(url) as response:
                if response.status == 200:
                    image = await response.read()
                    print(f"saving image {key}")
                    await save_images(image, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES)
                else:
                    print(f"Failed to download image: {url}")
        else:
            print(f"image {key} already exists, skipping...")
        url = f'{IMAGE_FOLDER}/{image_name}'
        return {key: url}

async def save_images(image, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES):
    if os.path.exists(image_path) and not OVERWRITE_IMAGES:
        print(f"image {key} already saved, skipping...")
        return
    image = Image.open(io.BytesIO(image)).convert("RGB")
    image.save(image_path, format='WEBP', quality=IMAGE_QUALITY)

async def process_images(urls, IMAGE_PATH, IMAGE_QUALITY, RATE_LIMIT, IMAGE_FOLDER, OVERWRITE_IMAGES):
    print("processing images....")
    semaphore = asyncio.Semaphore(RATE_LIMIT)
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url, key, semaphore, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES) for key, url in urls.items()]
        result = await asyncio.gather(*tasks)
    new_urls = {k:v for r in result for k, v in r.items()}
    return new_urls
