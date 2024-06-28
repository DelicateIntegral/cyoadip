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

### Configuration Parameters

- `DIRECTORY_PATH`: Optional.The directory path where the JSON file (`PROJECT_FILE`) and output JSON (`OUTPUT_FILE`) will be stored, and where the `IMAGE_FOLDER` for downloaded images will reside. Default is current working directory.
- `PROCESS_DISCORD_LINKS`: Optional. If set to `True`, it will process Discord links present in the JSON. Default is `False`. If `DOWNLOAD_IMAGES` is `True`, it will download images to `IMAGE_FOLDER` and update links like this: `IMAGE_FOLDER/image_name`. Otherwise, it will just refresh URLs and replace old ones.
- `TOKEN`: Optional but required if `PROCESS_DISCORD_LINKS` is `True`. Default is `YOUR TOKEN`. Your Discord bot token required for authentication with Discord's API.
- `PROJECT_FILE`: Optional. Default is `project.json`. The name of the input ICC JSON file containing Discord links.
- `OUTPUT_FILE`: Optional. Default is `project_new.json`. The name of the output JSON file where updated ICC JSON data will be saved.
- `IMAGE_FOLDER`: Optional. Default is `images`. The name of the folder where downloaded images will be stored within `DIRECTORY_PATH`.
- `IMAGE_QUALITY`: Optional. Default is `90`. The image quality of the webp images saved in `IMAGE_FOLDER`. Value between 0-100. Default is 90.
- `UPDATE_PREFIXES`: Optional. Default is `False`. If set to `True`, it will update image URLs by replacing `OLD_PREFIX` with `NEW_PREFIX`. Helpful if you have some folder of images in a server with constant prefix and you moved that folder to another server.
- `OLD_PREFIX`: Optional. Default is `""`. The old prefix to replace in image URLs. When it is not blank, only those urls which contain the `OLD_PREFIX` are changed to `NEW_PREFIX`.
- `NEW_PREFIX`: Optional. Default is `""`. The new prefix to prepend to updated image URLs. Leave blank if you are uploading `IMAGE_FOLDER` to Neocities or GitHub in the same directory as `index.html`.
- `MINIFY`: Optional. Default is `False`. Set to `True` to minify the output JSON file.
- `RATE_LIMIT`: Optional. Default is `2`. The maximum number of concurrent requests allowed for image download and URL refresh operations. Recommended 2 for discord link processing due to its api's rate limiting issue.
- `PROCESS_BASE64_IMAGES`: Optional. Default is `False`. If set to `True`, it will process base64 encoded images in the JSON, converting them to webp and storing to `IMAGE_FOLDER` and updating links like this: `IMAGE_FOLDER/image_name`.  You can provide `NEW_PREFIX` and set `UPDATE_PREFIXES` to `True` to update links to this: `NEW_PREFIX/IMAGE_FOLDER/image_name`.
- `DOWNLOAD_IMAGES`: Optional. Default is `False`. If set to `True`, it will download images linked in the JSON to `IMAGE_FOLDER` and updating links like this: `IMAGE_FOLDER/image_name`. You can provide `NEW_PREFIX` and set `UPDATE_PREFIXES` to `True` to update links to this: `NEW_PREFIX/IMAGE_FOLDER/image_name`.
- `OVERWRITE_IMAGES`: Optional. Default is `False`. If set to `True`, it will overwrite existing images in `IMAGE_FOLDER` otherwise skip pre-existing webp images.
- `DISABLE_IMAGES`: Optional. Default is `False`. If set to `True`, it will disable all images in the JSON and exit. All other parameters beside `DIRECTORY_PATH, PROJECT_FILE, OUTPUT_FILE, MINIFY` are ignored.

### Example Usage

```yaml
# Example config.yaml

DIRECTORY_PATH: "/home/myusername/cyoas/mycyoa/"
PROCESS_DISCORD_LINKS: True
TOKEN: "myvalidtoken"
OUTPUT_FILE: "output.json"
IMAGE_FOLDER: "myimages"
IMAGE_QUALITY: 60
NEW_PREFIX: "https://mysite.neocities.org/cyoas/mycyoa/"
MINIFY: True
UPDATE_PREFIXES: True
PROCESS_BASE64_IMAGES: True
DOWNLOAD_IMAGES: True
```

```bash
cyoatools --config="/home/myusername/cyoas/mycyoa/config.yaml"
```

**If you don't provide a config path, the script tries to get it from the current working directory.**

## Output

After running `cyoatools` with the above example configuration, it will:

- Process `config.yaml` and get config values
- Read the `project.json` file
- Process discord links as it is `True`. It traverses json file and generates the `choice id : url` map.
- Use the `TOKEN` to refresh urls from the map. `DOWNLOAD_IMAGES` is `True` so it downloads the images with name `image_{choice id}.webp` in the `myimages` with quality `60` and updates the links to `myimages/image_{choice id}.webp` for every `choice id` in map.
- `PROCESS_BASE64_IMAGES` is `True`, so it traverses json file and generates `choice id : base64 string` map. It converts them to webp with name `image_{choice id}.webp` in the `myimages` and updates the links to `myimages/image_{choice id}.webp` for every `choice id` in map.
- `DOWNLOAD_IMAGES` is `True`, so it is processes any other url other than discord links, creates map, downloads images and updates the link similar to in discord process.
- `UPDATE_PREFIXES` is `True` so it traverses json and updates link something like this: `if OLD_PREFIX in LINK then NEW_LINK = NEW_PREFIX + [Suffix in LINK after removing OLD_PREFIX]`.
- `MINIFY` is `True`, so it writes `output.json` minified in `DIRECTORY_PATH`.
- `DIRECTORY_PATH/myimages`: Folder containing downloaded images associated with the refreshed URLs and converted from base64 embeds.
