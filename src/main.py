import os

import supervisely as sly
import supervisely.app.development as sly_app_development
from supervisely.app.widgets import Container

import src.globals as g
from src.ui import container as ui_card

# Preparing the layout of the application and creating the application itself.
layout = Container(widgets=[ui_card])
app = sly.Application(layout=layout)

# Enabling advanced debug mode.
if sly.is_development():
    sly_app_development.supervisely_vpn_network(action="up")
    sly_app_development.create_debug_task(g.team_id, port="8000")


# Subscribing to the event of changing the selected frame in the Video Labeling Tool.
@app.event(sly.Event.ManualSelected.VideoChanged)
def video_changed(event_api: sly.Api, event: sly.Event.ManualSelected.VideoChanged):
    sly.logger.info("Current video was changed")
    # Saving the event parameters to global variables.
    g.api = event_api
    g.team_id = event.team_id
    g.session_id = event.session_id
    g.dataset_id = event.dataset_id
    g.video_id = event.video_id
    g.project_id = event.project_id
    g.frame = event.frame

    if event.project_id not in g.project_metas:
        project_meta = sly.ProjectMeta.from_json(g.api.project.get_meta(event.project_id))
        g.project_metas[event.project_id] = project_meta

    # Using a simple caching mechanism to avoid downloading the project meta every time.
    # is it necessary to download the annotations?
    if event.video_id not in g.annotations:
        ann_json = g.api.video.annotation.download(g.video_id)
        ann_path = os.path.join(sly.app.get_data_dir(), f"{g.video_id}_ann.json")
        sly.fs.silent_remove(ann_path)
        sly.json.dump_json_file(ann_json, ann_path)
        g.annotations[event.video_id] = ann_path


# TODO: will work after adding the event in the Labeling Tool and SDK
# # Subscribing to the event of changing the selected frame in the Video Labeling Tool.
# @app.event(sly.Event.ManualSelected.FrameChanged)
# def video_changed(event_api: sly.Api, event: sly.Event.ManualSelected.VideoChanged):
#     sly.logger.info("Current video was changed")
#     # Saving the event parameters to global variables.
#     g.api = event_api
#     g.team_id = event.team_id
#     g.session_id = event.session_id
#     g.dataset_id = event.dataset_id
#     g.video_id = event.video_id
#     g.project_id = event.project_id
#     g.frame = event.frame

#     # Using a simple caching mechanism to avoid downloading the project meta every time.
#     if event.project_id not in g.project_metas:
#         project_meta = sly.ProjectMeta.from_json(g.api.project.get_meta(event.project_id))
#         g.project_metas[event.project_id] = project_meta
