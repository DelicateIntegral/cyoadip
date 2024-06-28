import io
import os
import base64
import asyncio
import aiohttp
from PIL import Image
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn

console = Console()

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
            async with session.get(url) as response:
                if response.status == 200:
                    image = await response.read()
                    # print(f"saving image {key}")
                    await save_images(image, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES)
                else:
                    console.print(f"[bold red]Failed to download image: {url}")

        url = f'{IMAGE_FOLDER}/{image_name}'
        return {key: url}

async def save_images(image, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES):
    if os.path.exists(image_path) and not OVERWRITE_IMAGES:
        return
    image = Image.open(io.BytesIO(image)).convert("RGB")
    image.save(image_path, format='WEBP', quality=IMAGE_QUALITY)

async def process_images(urls, IMAGE_PATH, IMAGE_QUALITY, RATE_LIMIT, IMAGE_FOLDER, OVERWRITE_IMAGES):
    semaphore = asyncio.Semaphore(RATE_LIMIT)

    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url, key, semaphore, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES) for key, url in urls.items()]
        
        with Progress(
            TextColumn("{task.description}", justify="left", style="bold dark_orange3"),
            BarColumn(bar_width=40, style="bold red", complete_style="bold blue", finished_style="bold blue"),
            TextColumn("{task.completed}/{task.total}", style="bold dark_orange3"),
            SpinnerColumn(style="bold dark_green"),
            TextColumn("{task.percentage:>3.0f}%", style="bold dark_green")
        ) as progress:
            task = progress.add_task("Processing Image URLs", total=len(tasks))
            results = []
            for result in asyncio.as_completed(tasks):
                results.append(await result)
                progress.update(task, advance=1)

    new_urls = {k:v for r in results for k, v in r.items()}
    return new_urls
