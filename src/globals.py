import os

import supervisely as sly
from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

# Initializing global variables.
spawn_api_token = sly.env.spawn_api_token()
api = sly.Api.from_env()
spawn_api = sly.Api(server_address=api.server_address, token=spawn_api_token)
team_id = sly.env.team_id()

is_my_labeling_job = False
job_id = None
allowed_classes = None
allowed_tags = None

session_id = None
video_id = None
project_id = None
frame = None

session = None
task_type = None
model_session_id = None
model_meta = None
inference_settings = None
selected_classes = None
selected_tags = None
suffix = None
use_suffix = None

# We will store project meta in a dictionary so that we do not have to download it every time.
project_metas = {}
