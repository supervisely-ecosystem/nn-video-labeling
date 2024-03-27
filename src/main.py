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
        if frame is not None:
            g.frame = frame
            apply_button_clicked()


@server.post("/jobs.info")
def wrapper(request: Request):
    print("jobs.info was called")
    event_api = request.state.api
    context = request.state.context
    me = event_api.user.get_my_info()
    if not me:
        sly.logger.warning("Can't get annotator user info.")
        return
    if me.login == context.get("labelerLogin"):
        sly.logger.info(f"Labeler {me.login} is annotating the job.")
        g.is_my_labeling_job = True
        job_meta = context.get(ApiField.META, {})
        dynamic_classes = job_meta.get("dynamicClasses", False)
        dynamic_tags = job_meta.get("dynamicTags", False)
        g.is_dynamic_classes_tags = dynamic_classes or dynamic_tags
        if not g.is_dynamic_classes_tags:
            sly.logger.warning("Dynamic classes/tags are disabled. Enable it in the job settings.")
            error_text.text = "Dynamic classes/tags are disabled. Enable it in the job settings."
            error_text.show()
        else:
            error_text.hide()
            g.allowed_classes = [c.name for c in job_meta.get(ApiField.CLASSES, [])]
            g.allowed_tags = [t.name for t in job_meta.get(ApiField.TAGS, [])]
