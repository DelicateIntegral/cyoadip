# cyoatools

`cyoatools` is a Python package designed for processing ICC JSON files in a variety of ways.

## Installation

Install from source:

```bash
git clone https://github.com/DelicateIntegral/cyoatools.git
cd cyoatools
pip install .
```

## Usage

To use `cyoatools`, you need to provide a configuration YAML file (`config.yaml`):

```yaml
# Example config.yaml

DIRECTORY_PATH: "/path/to/your/directory/where/json/file/is"
PROCESS_DISCORD_LINKS: True
TOKEN: "YOUR TOKEN"
PROJECT_FILE: "project.json"
OUTPUT_FILE: "project_new.json"
IMAGE_FOLDER: "images"
IMAGE_QUALITY: 90
OLD_PREFIX: ""
NEW_PREFIX: ""
MINIFY: True
RATE_LIMIT: 2
UPDATE_PREFIXES: False
PROCESS_BASE64_IMAGES: True
DOWNLOAD_IMAGES: True
OVERWRITE_IMAGES: False
```

### Configuration Parameters

- `DIRECTORY_PATH`: The directory path where the JSON file (`PROJECT_FILE`) and output JSON (`OUTPUT_FILE`) will be stored, and where the `IMAGE_FOLDER` for downloaded images will reside.
- `PROCESS_DISCORD_LINKS`: If set to `True`, it will process Discord links present in the JSON. If `DOWNLOAD_IMAGES` is `True`, it will download images to `IMAGE_FOLDER` and update links like this: `IMAGE_FOLDER/image_name`. Otherwise, it will just refresh URLs and replace old ones. 
- `TOKEN`: Your Discord bot token required for authentication with Discord's API.
- `PROJECT_FILE`: The name of the input ICC JSON file containing Discord links.
- `OUTPUT_FILE`: The name of the output JSON file where updated ICC JSON data will be saved.
- `IMAGE_FOLDER`: The name of the folder where downloaded images will be stored within `DIRECTORY_PATH`.
- `IMAGE_QUALITY`: The image quality of the webp images saved in `IMAGE_FOLDER`. Value between 0-100. Default is 90.
- `UPDATE_PREFIXES`: Optional. If set to `True`, it will update image URLs by replacing `OLD_PREFIX` with `NEW_PREFIX`. Helpful if you have some folder of images in a server with constant prefix and you moved that folder to another server.
- `OLD_PREFIX`: Optional. The old prefix to replace in image URLs.
- `NEW_PREFIX`: Optional. The new prefix to prepend to updated image URLs. Leave blank if you are uploading `IMAGE_FOLDER` to Neocities or GitHub in the same directory as `index.html`.
- `MINIFY`: Optional. Set to `True` to minify the output JSON file.
- `RATE_LIMIT`: The maximum number of concurrent requests allowed for image download and URL refresh operations. Recommended 2 for now due to discord rate limiting issue.
- `PROCESS_BASE64_IMAGES`: If set to `True`, it will process base64 encoded images in the JSON, converting them to webp and storing to `IMAGE_FOLDER` and updating links like this: `IMAGE_FOLDER/image_name`.
- `DOWNLOAD_IMAGES`: If set to `True`, it will download images linked in the JSON to `IMAGE_FOLDER`.
- `OVERWRITE_IMAGES`: If set to `True`, it will overwrite existing images in `IMAGE_FOLDER` otherwise skip pre-existing webp images.

### Example Usage

```bash
cyoatools --config="/path/to/config.yaml"
```

If you don't provide a config path, the script tries to get it from the current working directory.

## Output

After running `cyoatools` with the above example configuration, it will generate:
- `project_new.json`: Updated ICC JSON file.
- `DIRECTORY_PATH/images`: Folder containing downloaded images associated with the refreshed URLs and converted from base64 embeds.
