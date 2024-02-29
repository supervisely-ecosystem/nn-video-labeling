import os

import supervisely as sly
from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

# Initializing global variables.
api = sly.Api.from_env()
team_id = sly.env.team_id()

session_id = None
video_id = None
project_id = None
frame = None

session = None
model_session_id = None
model_meta = None
inference_settings = None
selected_classes = None
selected_tags = None
suffix = None
use_suffix = None

# We will store project meta in a dictionary so that we do not have to download it every time.
project_metas = {}
