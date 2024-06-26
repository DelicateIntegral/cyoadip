import asyncio
import aiohttp
from cyoatools.process_json import get_urls, update_urls
from cyoatools.process_image import process_images

async def refresh_url(session, url, key, TOKEN, semaphore):
    print(f"refreshing url of image for choice id: {key}")
    async with semaphore:
        api_url = "https://discord.com/api/v9/attachments/refresh-urls"
        payload = {'attachment_urls': [url]}
        headers = {'Authorization': f'Bot {TOKEN}'}
    
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status == 200:
                refreshed_urls = await response.json()
                url = refreshed_urls['refreshed_urls'][0]['refreshed']
            else:
                print(f"Failed to refresh URL: {url}")
    return {key: url}     

async def process_refresh(urls, TOKEN, RATE_LIMIT):
    semaphore = asyncio.Semaphore(RATE_LIMIT)
    async with aiohttp.ClientSession() as session:
        tasks = [refresh_url(session, url, key, TOKEN, semaphore) for key, url in urls.items()]
        result = await asyncio.gather(*tasks)
    new_urls = {k:v for r in result for k, v in r.items()}
    return new_urls

async def process_discord(data, DOWNLOAD_IMAGES, TOKEN, OVERWRITE_IMAGES, RATE_LIMIT, IMAGE_FOLDER, IMAGE_QUALITY, IMAGE_PATH):
    
    print("finding existing urls...")
    urls = get_urls(data, True)
    print("refreshing urls...")
    new_urls = await process_refresh(urls, TOKEN, RATE_LIMIT)

    if DOWNLOAD_IMAGES:
        new_urls = await process_images(new_urls, IMAGE_PATH, IMAGE_QUALITY, RATE_LIMIT, IMAGE_FOLDER, OVERWRITE_IMAGES)
    
    discord_data = update_urls(data, new_urls)
    return discord_data