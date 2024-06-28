import os
import asyncio
import yaml
import argparse
from cyoatools.process_json import read_json, write_json, process_base64, update_prefixes, get_urls, update_urls, disable_images
from cyoatools.process_image import process_images, console
from cyoatools.process_discord import process_discord

async def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Image Processor for ICC JSONS')
    parser.add_argument('--config', type=str, default=None, help='Path to the configuration YAML file')
    args = parser.parse_args()

    if args.config is None:
        args.config = os.path.join(os.getcwd(), 'config.yaml')

    # Read configurations from YAML file
    with open(args.config, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)

    # Extract variables from the config
    DIRECTORY_PATH = config.get('DIRECTORY_PATH', os.getcwd())
    PROCESS_DISCORD_LINKS = config.get('PROCESS_DISCORD_LINKS', False)
    TOKEN = config.get('TOKEN', 'YOUR TOKEN')
    PROCESS_BASE64_IMAGES = config.get('PROCESS_BASE64_IMAGES', False)
    OLD_PREFIX = config.get('OLD_PREFIX', '')
    NEW_PREFIX = config.get('NEW_PREFIX', '')
    UPDATE_PREFIXES = config.get('UPDATE_PREFIXES', False)
    DOWNLOAD_IMAGES = config.get('DOWNLOAD_IMAGES', False)
    RATE_LIMIT = config.get('RATE_LIMIT', 2)
    IMAGE_FOLDER = config.get('IMAGE_FOLDER', 'images')
    IMAGE_QUALITY = config.get('IMAGE_QUALITY', 90)
    OVERWRITE_IMAGES = config.get('OVERWRITE_IMAGES', False)
    PROJECT_FILE = config.get('PROJECT_FILE', 'project.json')
    OUTPUT_FILE = config.get('OUTPUT_FILE', 'project_new.json')
    MINIFY = config.get('MINIFY', False)
    DISABLE_IMAGES = config.get('DISABLE_IMAGES', False)
    

    PROJECT_PATH = os.path.join(DIRECTORY_PATH, PROJECT_FILE)
    IMAGE_PATH = os.path.join(DIRECTORY_PATH, IMAGE_FOLDER)
    OUTPUT_PATH = os.path.join(DIRECTORY_PATH, OUTPUT_FILE)
    
    console.print("[blue]Reading JSON Data...")
    data = read_json(PROJECT_PATH)

    if data == "Error: File not found":
        console.print("[bold red]Error: File not found")
        return

    if os.path.exists(OUTPUT_PATH):
        console.print("[bold red]Removing Existing Output JSON...")
        os.remove(OUTPUT_PATH)

    if DISABLE_IMAGES:
        data = disable_images(data)
        write_json(OUTPUT_PATH, data, MINIFY)
        return

    console.print("[blue]Checking/Creating Image Folder...")
    os.makedirs(IMAGE_PATH, exist_ok=True)
    
    if PROCESS_DISCORD_LINKS:
        console.print("[blue]Processing Discord Links...")
        data = await process_discord(data, DOWNLOAD_IMAGES, TOKEN, OVERWRITE_IMAGES, RATE_LIMIT, IMAGE_FOLDER, IMAGE_QUALITY, IMAGE_PATH)
    
    if PROCESS_BASE64_IMAGES:
        new_urls = await process_base64(data, IMAGE_PATH, IMAGE_FOLDER, IMAGE_QUALITY, OVERWRITE_IMAGES)
        update_urls(data, new_urls)

    if DOWNLOAD_IMAGES:
        urls = get_urls(data)
        new_urls = await process_images(urls, IMAGE_PATH, IMAGE_QUALITY, RATE_LIMIT, IMAGE_FOLDER, OVERWRITE_IMAGES)
        update_urls(data, new_urls)
    
    if UPDATE_PREFIXES:
        data = update_prefixes(data, NEW_PREFIX, OLD_PREFIX)
    
    write_json(OUTPUT_PATH, data, MINIFY)

if __name__ == "__main__":
    asyncio.run(main())
