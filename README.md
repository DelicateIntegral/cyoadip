# cyoadip

`cyoadip` (short for "CYOA Discord Image Processor") is a Python package designed for refreshing Discord links found in ICC JSON files. It retrieves refreshed URLs using Discord's API and updates the JSON data accordingly. Additionally, it downloads images associated with these links into a specified directory path.

## Installation

Install from source:

```bash
git clone https://github.com/your-username/cyoadip.git
cd cyoadip
pip install .
```

## Usage

To use `cyoadip`, you need to provide a configuration YAML file (`config.yaml`):

```yaml
# Example config.yaml

DIRECTORY_PATH: "/path/to/your/directory/containing/json"
TOKEN: "YOUR_DISCORD_BOT_TOKEN"
PROJECT_FILE: "project.json"
OUTPUT_FILE: "project_new.json"
IMAGE_FOLDER: "images"
NEW_PREFIX: "https://example.com/new_prefix"
MINIFY: false
RATE_LIMIT: 2
```

### Configuration Parameters

- `DIRECTORY_PATH`: The directory path where the JSON file (`PROJECT_FILE`) and output JSON (`OUTPUT_FILE`) will be stored, and where the `IMAGE_FOLDER` for downloaded images will reside.
- `TOKEN`: Your Discord bot token required for authentication with Discord's API.
- `PROJECT_FILE`: The name of the input ICC JSON file containing Discord links.
- `OUTPUT_FILE`: The name of the output JSON file where updated ICC JSON data will be saved.
- `IMAGE_FOLDER`: The name of the folder where downloaded images will be stored within `directory_path`.
- `NEW_PREFIX`: Optional. The new prefix to prepend to updated image URLs.
- `MINIFY`: Optional. Set to `true` to minify the output JSON file.
- `RATE_LIMIT`: The maximum number of concurrent requests allowed for image download and URL refresh operations. Recommended 2 for now.

### Example Usage

```bash
cyoadip --config="/path/to/config.yaml"
```
If you don't provide a config path the script tries to get it in current working directory.

## Output

After running `cyoadip` with your configuration, it will generate:
- `project_new.json`: Updated ICC JSON file with refreshed Discord URLs.
- `images/`: Folder containing downloaded images associated with the refreshed URLs.