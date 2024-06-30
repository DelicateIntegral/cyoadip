import io
import os
import base64
import asyncio
import aiohttp
from PIL import Image
from rich.console import Console, Group
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.live import Live
from rich.rule import Rule
from rich.layout import Layout
from rich.panel import Panel

console = Console()

async def base64_to_webp(base64_string, key, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES):
    image_data = base64.b64decode(base64_string.split(",")[1])
    image_name = f'image_{key}.webp'
    image_path = os.path.join(IMAGE_PATH, image_name)
    await save_images(image_data, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES)
    url = f'{IMAGE_FOLDER}/{image_name}'
    return {key: url}

async def download_image(session, url, key, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES, download_progress, failed, semaphore):
    image_name = f'image_{key}.webp'
    image_path = os.path.join(IMAGE_PATH, image_name)
    async with semaphore:
        if (not os.path.exists(image_path)) or OVERWRITE_IMAGES:
            async with session.get(url) as response:
                if response.status == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    task_id = download_progress.add_task(f"Downloading Image {key}", total=total_size, filename=image_name)
                    image_data = bytearray()
                    chunk_size = 1024
                    async for chunk in response.content.iter_chunked(chunk_size):
                        image_data.extend(chunk)
                        download_progress.update(task_id, advance=len(chunk))
                    await save_images(image_data, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES)
                    download_progress.remove_task(task_id)
                else:
                    failed.append(f"[bold red]Failed to download image for choice id {key}: {url}, status: {response.status}")
                    return {key: url}

    url = f'{IMAGE_FOLDER}/{image_name}'
    return {key: url}

async def save_images(image, key, image_path, IMAGE_QUALITY, OVERWRITE_IMAGES):
    if os.path.exists(image_path):
        if OVERWRITE_IMAGES:
            os.remove(image_path)
        else:
            return
    image = Image.open(io.BytesIO(image)).convert("RGB")
    image.save(image_path, format='WEBP', quality=IMAGE_QUALITY)

async def process_images(urls, IMAGE_PATH, IMAGE_QUALITY, IMAGE_FOLDER, OVERWRITE_IMAGES, DOWNLOAD_RATE_LIMIT):
    semaphore = asyncio.Semaphore(DOWNLOAD_RATE_LIMIT)
    
    async with aiohttp.ClientSession() as session:
        
        task_progress = Progress(
            TextColumn("{task.description}", justify="left", style="bold dark_orange3"),
            BarColumn(bar_width=40, style="bold red", complete_style="bold blue", finished_style="bold blue"),
            TextColumn("{task.completed}/{task.total}", style="bold dark_orange3"),
            SpinnerColumn(style="bold dark_green"),
            TextColumn("{task.percentage:>3.0f}%", style="bold dark_green")
        )
        
        download_progress = Progress(
            TextColumn("[bold yellow]Downloading {task.fields[filename]}"),
            BarColumn(),
            DownloadColumn()
        )

        group = Group(
            # Rule(style='#AAAAAA'),
            task_progress,
            download_progress
        )

        failed = []
        tasks = [download_image(session, url, key, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES, download_progress, failed, semaphore) for key, url in urls.items()]
        task = task_progress.add_task("Downloading Images", total=len(tasks))

        with Live(Panel(Layout(group), border_style="bold blue", width=80, height=12, style="bold blue"), refresh_per_second=10, vertical_overflow="visible") as livepanel:
            results = []
            fsize = len(failed)
            for result in asyncio.as_completed(tasks):
                results.append(await result)
                if len(failed) > fsize:
                    fsize = len(failed)
                else:
                    task_progress.update(task, advance=1)
            livepanel.update(Panel(Layout(group), border_style="bold blue", width=80, height=3)) 
    
    for f in failed:
        console.print(f"[bold red]{f}")
    
    new_urls = {k:v for r in results for k, v in r.items()}
    return new_urls
