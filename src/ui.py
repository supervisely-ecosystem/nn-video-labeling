import supervisely as sly
import yaml
from supervisely.app import widgets as w

import src.functions as f
import src.globals as g

# ACTIONS
select_session = w.SelectAppSession(g.team_id, ["deployed_nn"], size="small")
apply_button = w.Button(
    "Apply model to image", icon="zmdi zmdi-fire mr5", button_size="mini", button_type="success"
)
apply_button.hide()
model_box = w.Flexbox([select_session, apply_button])

connect_button = w.Button("Connect", icon="zmdi zmdi-check", button_size="small")
disconnect_button = w.Button(
    "Disconnect", icon="zmdi zmdi-close", button_type="danger", button_size="small"
)
disconnect_button.hide()
buttons_box = w.Flexbox([connect_button, disconnect_button])
icon = w.Field.Icon(
    zmdi_class="zmdi zmdi-compass", color_rgb=[44, 210, 110], bg_color_rgb=[216, 248, 231]
)

connect_field = w.Field(
    content=w.Container(
        [model_box, buttons_box], direction="horizontal", style="margin-top: 10px", overflow=None
    ),
    title="Connect to running model",
    description="Define session (task id) with deployed model and connect to it.",
    icon=icon,
)


# ERROR TEXT
error_text = w.Text(status="warning")
error_text.hide()

# MODEL INFO
model_info = w.ModelInfo()
classes_info_text = w.Text("List of classes from the model:", "text")
select_classes = w.ClassesListSelector(multiple=True)
classes_info = w.Container([classes_info_text, select_classes])

tags_info_text = w.Text("List of tags from the model:", "text")
select_tags = w.TagsListSelector(multiple=True)
tags_info = w.Container([tags_info_text, select_tags])

# INFERENCE SETTINGS
suffix_input = w.Input("model", placeholder="Enter suffix")
suffix_checkbox = w.Checkbox("Always add suffix to class/tag name")
suffix_field = w.Field(
    content=w.Container([suffix_input, suffix_checkbox]),
    title="Classes/Tags suffix",
    description="Add suffix to model class/tag name if it has conflicts with existing one",
)
inference_settings = w.Editor(height_lines=30)
settings_container = w.Container([suffix_field, inference_settings])

tabs = w.Tabs(
    labels=["Info", "Classes", "Tags", "Inference"],
    contents=[
        model_info,
        classes_info,
        tags_info,
        settings_container,
    ],
    type="card",
)
tabs.hide()

ui_content = w.Container([connect_field, error_text, tabs])


# @connect_button.click
def connect_button_clicked():
    """Connects to the selected model session and changes the UI state."""

    connect_button.loading = True
    g.model_session_id = select_session.get_selected_id()
    if g.model_session_id is None:
        error_text.text = "No model was selected, please select a model and try again."
        error_text.show()
        return

    g.session = sly.nn.inference.Session(g.api, task_id=g.model_session_id)
    session_info = g.session.get_session_info()
    g.task_type = session_info.get("task type")

    if not session_info:
        error_text.text = (
            "Couldn't connect to the model. Make sure that model is deployed and try again."
        )
        error_text.show()
        return

    model_info.set_model_info(g.model_session_id, session_info)

    # Get the model meta.
    g.model_meta = g.session.get_model_meta()

    # Load the inference settings from the model.
    g.inference_settings = yaml.dump(g.session.get_default_inference_settings(), allow_unicode=True)
    inference_settings.set_text(g.inference_settings, language_mode="yaml")

    # Load the classes and tags from the model metadata.
    g.selected_classes = f.load_classes(g.model_meta)
    select_classes.set(g.selected_classes)
    select_classes.select_all()
    g.selected_tags = f.load_tags(g.model_meta)
    select_tags.set(g.selected_tags)
    select_tags.select_all()

    select_session.hide()
    connect_button.hide()
    error_text.hide()
    connect_button.loading = False
    tabs.show()
    disconnect_button.show()
    apply_button.show()


@disconnect_button.click
def disconnect_button_click():
    """Changes the UI state when the model is changed."""

    disconnect_button.loading = True
    apply_button.hide()

    sly.logger.info(f"Disconnect from model session: {g.model_session_id}")
    g.model_session_id = None
    g.model_meta = None
    g.inference_settings = None
    g.session = None
    disconnect_button.loading = False
    disconnect_button.hide()
    tabs.hide()
    connect_button.show()
    select_session.show()


# @apply_button.click
def apply_button_clicked():
    """Applies the model to the selected image."""

    error_text.hide()
    apply_button.loading = True
    disconnect_button.disable()
    selected_classes = select_classes.get_selected_classes()
    selected_tags = select_tags.get_selected_tags()
    suffix = suffix_input.get_value()
    use_suffix = suffix_checkbox.is_checked()

    new_session = sly.nn.inference.Session(g.api, task_id=g.model_session_id)
    new_session_info = new_session.get_session_info()
    if g.task_type != new_session_info.get("task type"):
        error_text.text = "Model task type has been changed. Reconnecting..."
        error_text.show()
        connect_button_clicked()
        select_classes.select([obj_class.name for obj_class in selected_classes])
        select_tags.select([tag.name for tag in selected_tags])
        suffix_input.set_value(suffix)
        suffix_checkbox.check() if use_suffix else suffix_checkbox.uncheck()

    g.selected_classes = selected_classes
    g.selected_tags = selected_tags
    g.suffix = suffix
    g.use_suffix = use_suffix

    try:
        inf_settings = yaml.safe_load(inference_settings.get_value())
        print(f"Inference Settings: {inf_settings}")
    except Exception as e:
        inf_settings = yaml.safe_load(g.inference_settings)
        sly.logger.warning(
            f"Model Inference launched without additional settings. \n" f"Reason: {e}",
            exc_info=True,
        )
    g.session.set_inference_settings(inf_settings)
    g.spawn_api.vid_ann_tool.disable_job_controls(g.session_id)
    try:
        f.inference()
        print("Inference done.")
    except Exception as e:
        sly.logger.warning("Model Inference failed", exc_info=True)
        error_text.text = f"Model Inference failed: {repr(e)}"
        error_text.show()
    g.spawn_api.vid_ann_tool.enable_job_controls(g.session_id)
    disconnect_button.enable()
    apply_button.loading = False
