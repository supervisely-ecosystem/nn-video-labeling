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
dataset_id = None
video_id = None
project_id = None
frame = None
figure_id = None
object_id = None
figure_class_id = None
figure_class_name = None
timestamp = None

session = None
model_session_id = None
model_meta = None
inference_settings = None
selected_classes = None
selected_tags = None

# We will save video annotatioins locally and store in a dictionary paths so that we do not have to download it every time.
annotations = {}

# We will store project meta in a dictionary so that we do not have to download it every time.
project_metas = {}

# add_predictions_modes = ["merge with existing labels", "replace existing labels"]
