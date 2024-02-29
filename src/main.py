import supervisely as sly
import supervisely.app.development as sly_app_development
from fastapi import Request
from supervisely.app.widgets import Button, Container

import src.globals as g
from src.ui import apply_button, apply_button_clicked, ui_content

layout = Container(widgets=[ui_content])
app = sly.Application(layout=layout)
server = app.get_server()

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
    g.video_id = event.video_id
    g.project_id = event.project_id
    g.frame = event.frame

    if event.project_id not in g.project_metas:
        project_meta = sly.ProjectMeta.from_json(g.api.project.get_meta(event.project_id))
        g.project_metas[event.project_id] = project_meta


apply_button._click_handled = True


# * reimplementing the click event of the apply button to get the frame index from the context
@server.post(apply_button.get_route_path(Button.Routes.CLICK))
def apply_button_click(request: Request):
    state = request.get("state")
    if state:
        context = state.get("context")
        frame = context.get("frame")
        g.project_id = context.get("projectId", g.project_id)
        g.video_id = context.get("entityId", g.video_id)
        g.session_id = context.get("sessionId", g.session_id)

        if g.project_id:
            if g.project_id not in g.project_metas:
                project_meta = sly.ProjectMeta.from_json(g.api.project.get_meta(g.project_id))
                g.project_metas[g.project_id] = project_meta
        if frame:
            g.frame = frame
            apply_button_clicked()
