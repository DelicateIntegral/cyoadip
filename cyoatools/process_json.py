import asyncio
import json
from cyoatools.process_image import base64_to_webp

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_json(file_path, json_data, minify):
    with open(file_path, 'w', encoding='utf-8') as f:
        indent = None if minify else 2
        separators = (',', ':') if minify else None
        if minify:
            print("minifying json...")
        json.dump(json_data, f, indent=indent, separators=separators)

def get_urls(json_data, DISCORD_MODE = False):
    print("getting existing urls....")
    urls = {}
    def traverse(data):
        if isinstance(data, dict):
            choice_id = data.get("id")
            imageLink = data.get("imageLink", "")
            if choice_id is not None:
                if not DISCORD_MODE:
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
    print("Updating urls...")
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
    print("processing base64 images...")
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
    result = await asyncio.gather(*tasks)
    new_urls = new_urls = {k:v for r in result for k, v in r.items()}
    return new_urls

def update_prefixes(data, NEW_PREFIX, OLD_PREFIX):
    print("updating prefixes...")
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