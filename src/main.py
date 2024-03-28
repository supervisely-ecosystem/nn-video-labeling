import supervisely as sly
import supervisely.app.development as sly_app_development
from fastapi import Request
from supervisely.api.module_api import ApiField
from supervisely.app.widgets import Button, Container

import src.globals as g
from src.ui import apply_button, apply_button_clicked, error_text, ui_content

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
    error_text.hide()
    state = request.get("state")
    if state:
        context = state.get("context")
        job_id = context.get("jobId")
        g.is_my_labeling_job = False
        if job_id is None:
            g.job_id = None
            g.is_my_labeling_job = False
        elif g.job_id != job_id:
            me = g.api.user.get_my_info()
            lableing_job = g.spawn_api.labeling_job.get_info_by_id(job_id)
            if not me:
                sly.logger.warning("Can't get annotator user info.")
                g.job_id = None
            elif me.id == lableing_job.assigned_to_id:
                g.is_my_labeling_job = True
                g.allowed_classes = lableing_job.classes_to_label
                g.allowed_tags = lableing_job.tags_to_label
                g.job_id = job_id
                error_text.set(
                    "Labeling job detected. Some classes and tags can be restricted.", status="info"
                )
                error_text.show()
            else:
                g.job_id = None
                g.is_my_labeling_job = False
                error_text.set("", status="warning")
                error_text.hide()
        else:
            g.is_my_labeling_job = True

        frame = context.get("frame")
        g.project_id = context.get("projectId", g.project_id)
        g.video_id = context.get("entityId", g.video_id)
        g.session_id = context.get("sessionId", g.session_id)

        if g.project_id:
            if g.project_id not in g.project_metas:
                project_meta = sly.ProjectMeta.from_json(g.api.project.get_meta(g.project_id))
                g.project_metas[g.project_id] = project_meta
        if frame is not None:
            g.frame = frame
            apply_button_clicked()
