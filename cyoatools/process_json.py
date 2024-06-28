import asyncio
import json
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from cyoatools.process_image import base64_to_webp, console

def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return "Error: File not found"

def write_json(file_path, json_data, minify):
    with open(file_path, 'w', encoding='utf-8') as f:
        indent = None if minify else 2
        separators = (',', ':') if minify else None
        if minify:
            console.print("[blue]Minifying JSON...")
        console.print("[blue]Writing Output JSON...")
        json.dump(json_data, f, indent=indent, separators=separators)

def get_urls(json_data, DISCORD_MODE = False):
    urls = {}
    def traverse(data):
        if isinstance(data, dict):
            choice_id = data.get("id")
            imageLink = data.get("imageLink", "")
            if choice_id is not None:
                if not DISCORD_MODE and "http" in imageLink and not "discordapp" in imageLink:
                    urls[choice_id] = data["imageLink"]
                elif "discordapp" in imageLink:
                    urls[choice_id] = data["imageLink"]
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    traverse(value)
        elif isinstance(data, list):
            for item in data:
                traverse(item)
    traverse(json_data)
    return urls

def update_urls(json_data, url_map):
    def traverse_and_modify(data):
        if isinstance(data, dict):
            choice_id = data.get("id")
            if choice_id is not None and url_map.get(choice_id) is not None:
                data["image"] = url_map[choice_id]
                data["imageLink"] = url_map[choice_id]
                data["imageIsUrl"] = True
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    traverse_and_modify(value)
        elif isinstance(data, list):
            for item in data:
                traverse_and_modify(item)
    traverse_and_modify(json_data)
    return json_data



async def process_base64(json_data, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES):
    base64map = {}
    
    def traverse_and_modify(data):
        if isinstance(data, dict):
            choice_id = data.get("id")
            image = data.get("image")
            if choice_id is not None and image is not None and image.startswith("data:image/"):
                base64map[choice_id] = image
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    traverse_and_modify(value)
        elif isinstance(data, list):
            for item in data:
                traverse_and_modify(item)
    
    traverse_and_modify(json_data)
    tasks = [base64_to_webp(image, key, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES) for key, image in base64map.items()]

    with Progress(
        TextColumn("{task.description}", justify="left", style="bold dark_orange3"),
        BarColumn(bar_width=40, style="bold red", complete_style="bold blue", finished_style="bold blue"),
        TextColumn("{task.completed}/{task.total}", style="bold dark_orange3"),
        SpinnerColumn(style="bold dark_green"),
        TextColumn("{task.percentage:>3.0f}%", style="bold dark_green")
    ) as progress:
        task = progress.add_task("Processing Base64 Images", total=len(tasks))
        results = []
        for result in asyncio.as_completed(tasks):
            results.append(await result)
            progress.update(task, advance=1)
    
    new_urls = {k:v for r in results for k, v in r.items()}
    return new_urls

def update_prefixes(data, NEW_PREFIX, OLD_PREFIX):
    console.print("[blue] Updating Prefixes...")
    def traverse_and_modify(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["image", "imageLink"] and isinstance(value, str) and value.startswith(OLD_PREFIX):
                    data[key] = NEW_PREFIX + value[len(OLD_PREFIX):]
                elif isinstance(value, dict) or isinstance(value, list):
                    traverse_and_modify(value)
        elif isinstance(data, list):
            for item in data:
                traverse_and_modify(item)
    
    traverse_and_modify(data)
    return data

def disable_images(json_data):
    console.print("[blue]Disabling all images in JSON...")
    def traverse_and_modify(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["image", "backgroundImage", "objectBackgroundImage", "rowBackgroundImage", "imageLink"]:
                    data[key] = ""
                elif key in ["imageIsUrl", "objectImgBorderIsOn"]:
                    data[key] = False
                elif isinstance(value, dict) or isinstance(value, list):
                    traverse_and_modify(value)
        elif isinstance(data, list):
            for item in data:
                traverse_and_modify(item)
    
    traverse_and_modify(json_data)
    return json_data