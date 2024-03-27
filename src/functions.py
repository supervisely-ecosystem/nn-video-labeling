from typing import Dict, Literal, Tuple, Union

import supervisely as sly
import yaml

import src.globals as g


def connect_to_model(api: sly.Api, model_session_id: int) -> bool:
    """Connects to the selected model session.

    :return: True if the connection was successful, False otherwise.
    :rtype: bool
    """
    try:
        session_info = api.task.send_request(
            model_session_id, "get_session_info", data={}, timeout=3
        )
        sly.logger.info(f"Connected to model session: {session_info}")
        return session_info
    except Exception as e:
        sly.logger.warning(
            f"Couldn't get model info. Make sure that model is deployed and try again. Reason: {e}"
        )
        return None


def get_model_meta(api: sly.Api, model_session_id: int) -> sly.ProjectMeta:
    """Returns model meta in Supervisely format.

    :return: Model meta in Supervisely format.
    :rtype: sly.ProjectMeta
    """
    meta_json = api.task.send_request(model_session_id, "get_output_classes_and_tags", data={})
    return sly.ProjectMeta.from_json(meta_json)


def get_inference_settings(api: sly.Api, model_session_id: int) -> str:
    """Returns custom inference settings for the model.
    The settings are returned as a string in YAML format.

    :return: Custom inference settings for the model.
    :rtype: str
    """
    inference_settings = api.task.send_request(
        model_session_id, "get_custom_inference_settings", data={}
    )
    inference_settings = inference_settings.get("settings")
    if inference_settings is None or len(inference_settings) == 0:
        inference_settings = ""
        sly.logger.info("Model doesn't support custom inference settings.")
    elif isinstance(inference_settings, dict):
        inference_settings = yaml.dump(inference_settings, allow_unicode=True)
    sly.logger.info(f"Inference settings: {inference_settings}")
    return inference_settings


def load_classes(model_meta) -> sly.ObjClassCollection:
    """Fills the widget with the classes from the model metadata."""
    if g.is_my_labeling_job:
        obj_classes = []
        for obj_class in model_meta.obj_classes:
            if obj_class.name in g.allowed_classes:
                obj_classes.append(obj_class)
    else:
        obj_classes = model_meta.obj_classes
    sly.logger.info(f"{len(obj_classes)} classes were loaded.")
    return obj_classes


def load_tags(model_meta) -> sly.TagMetaCollection:
    """Fills the widget with the tags from the model metadata."""
    if g.is_my_labeling_job:
        obj_tags = []
        for tag_meta in model_meta.tag_metas:
            if tag_meta.name in g.allowed_tags:
                obj_tags.append(tag_meta)
    else:
        obj_tags = model_meta.tag_metas
    sly.logger.info(f"{len(obj_tags)} tags were loaded.")
    return obj_tags


def inference():
    """Applies the model to the selected frame."""
    project_meta = g.project_metas[g.project_id]

    predictions_list = g.session.inference_video_id(
        g.video_id, start_frame_index=g.frame, frames_count=1, frames_direction="forward"
    )
    if len(predictions_list) == 1:
        ann = predictions_list[0]
        ann, res_project_meta = postprocess(
            ann, project_meta, g.selected_classes, g.selected_tags, g.suffix, g.use_suffix
        )
        if project_meta != res_project_meta:
            project_meta = res_project_meta
            g.spawn_api.project.update_meta(g.project_id, project_meta.to_json())
        g.api.project.pull_meta_ids(g.project_id, project_meta)
        g.project_metas[g.project_id] = project_meta

        video_objects = []
        for label in ann.labels:
            obj_class = project_meta.get_obj_class(label.obj_class.name)
            video_object = sly.VideoObject(obj_class, sly.VideoTagCollection())
            video_objects.append(video_object)
        ids = g.api.video.object.append_bulk(g.video_id, video_objects, sly.KeyIdMap())

        for label, obj_id in zip(ann.labels, ids):
            geometry_json = label.geometry.to_json()
            geometry_type = label.geometry.geometry_name()
            fig_id = g.api.video.figure.create(
                g.video_id, obj_id, g.frame, geometry_json, geometry_type
            )
            for tag in label.tags:
                tag_meta = project_meta.get_tag_meta(tag.meta.name)
                g.api.advanced.add_tag_to_object(tag_meta.sly_id, fig_id, tag.value)


def postprocess(
    ann: sly.Annotation,
    project_meta: sly.ProjectMeta,
    keep_classes: sly.ObjClassCollection,
    keep_tags: sly.TagMetaCollection,
    suffix: str,
    use_suffix: bool,
) -> Tuple[sly.Annotation, sly.ProjectMeta]:
    """Postprocesses annotation after model inference and returns the result annotation and project meta.
    Removes classes and tags that are not selected in the UI.

    :param ann: Annotation to postprocess.
    :type ann: sly.Annotation
    :param project_meta: Project meta.
    :type project_meta: sly.ProjectMeta
    :return: Result annotation, result project meta.
    :rtype: Tuple[sly.Annotation, sly.ProjectMeta]
    """

    res_project_meta, class_mapping, tag_meta_mapping = merge_metas(
        project_meta, keep_classes, keep_tags, suffix, use_suffix
    )
    keep_class_names = [obj_class.name for obj_class in keep_classes]
    keep_tag_names = [tag_meta.name for tag_meta in keep_tags]

    image_tags = []
    for tag in ann.img_tags:
        if tag.meta.name not in keep_tags:
            continue
        image_tags.append(tag.clone(meta=tag_meta_mapping[tag.meta.name]))

    new_labels = []
    for label in ann.labels:
        if label.obj_class.name not in keep_class_names:
            continue
        label_tags = []
        for tag in label.tags:
            if tag.meta.name not in keep_tag_names:
                continue
            label_tags.append(tag.clone(meta=tag_meta_mapping[tag.meta.name]))
        new_label = label.clone(
            obj_class=class_mapping[label.obj_class.name.strip()],
            tags=sly.TagCollection(label_tags),
        )
        new_labels.append(new_label)

    res_ann = ann.clone(labels=new_labels, img_tags=sly.TagCollection(image_tags))
    return res_ann, res_project_meta


def merge_metas(
    project_meta: sly.ProjectMeta,
    keep_classes: sly.ObjClassCollection,
    keep_tags: sly.TagMetaCollection,
    suffix: str,
    use_suffix: bool,
) -> Tuple[sly.ProjectMeta, Dict[str, sly.ObjClass], Dict[str, sly.TagMeta]]:
    result_meta = project_meta.clone()

    def _merge(
        result_meta: sly.ProjectMeta,
        data_type=Literal["class", "tag"],
        suffix: str = "model",
        use_suffix: bool = False,
    ):
        """Merges classes or tags from the model meta to the project meta.

        :param result_meta: Project meta to merge to.
        :type result_meta: sly.ProjectMeta
        :param data_type: Data type to merge (class or tag).
        :type data_type: Literal["class", "tag"]
        :return: Result project meta, mapping of the model classes/tags to the project classes/tags.
        :rtype: Tuple[sly.ProjectMeta, Dict[str, sly.ObjClass]]
        """
        if data_type == "class":
            project_collection = project_meta.obj_classes
            keep_names = [obj_class.name for obj_class in keep_classes]
            model_collection = g.model_meta.obj_classes
        else:
            project_collection = project_meta.tag_metas
            keep_names = [tag_meta.name for tag_meta in keep_tags]
            model_collection = g.model_meta.tag_metas
        mapping = {}
        for name in keep_names:
            model_item = model_collection.get(name)
            res_item, res_name = find_item(project_collection, model_item, suffix, use_suffix)
            if res_item is None:
                res_item = model_item.clone(name=res_name)
                result_meta = (
                    result_meta.add_obj_class(res_item)
                    if data_type == "class"
                    else result_meta.add_tag_meta(res_item)
                )
            mapping[model_item.name.strip()] = res_item
        return result_meta, mapping

    result_meta, class_mapping = _merge(
        result_meta,
        data_type="class",
        suffix=suffix,
        use_suffix=use_suffix,
    )
    result_meta, tag_mapping = _merge(
        result_meta,
        data_type="tag",
        suffix=suffix,
        use_suffix=use_suffix,
    )
    return result_meta, class_mapping, tag_mapping


def find_item(
    collection: Union[sly.ObjClassCollection, sly.TagMetaCollection],
    item: Union[sly.ObjClass, sly.TagMeta],
    suffix: str,
    use_suffix: bool,
) -> Tuple[Union[sly.ObjClass, sly.TagMeta], str]:
    """Finds an item in the collection and returns it or generates a new name for the item.

    :param collection: Collection to search in.
    :type collection: Union[sly.ObjClassCollection, sly.TagMetaCollection]
    :param item: Item to find.
    :type item: Union[sly.ObjClass, sly.TagMeta]
    :return: Found item, new name for the item.
    :rtype: Tuple[Union[sly.ObjClass, sly.TagMeta], str]
    """
    index = 0
    res_name = item.name.strip()
    while True:
        existing_item = collection.get(res_name.strip())
        if existing_item is None:
            if use_suffix is True:
                res_name = generate_res_name(item, suffix, index)
                existing_item = collection.get(res_name)
                if existing_item is not None:
                    return existing_item, None
            return None, res_name
        else:
            if existing_item == item.clone(name=res_name):
                if use_suffix is True:
                    res_name = generate_res_name(item, suffix, index)
                    existing_item = collection.get(res_name)
                    if existing_item is None:
                        return None, res_name
                    elif existing_item == item.clone(name=res_name):
                        res_name = generate_res_name(item, suffix, index)
                        existing_item = collection.get(res_name)
                        if existing_item is None:
                            return None, res_name
                        return existing_item, None
                    else:
                        index += 1
                        res_name = generate_res_name(item, suffix, index)
                        existing_item = collection.get(res_name)
                        if existing_item is None:
                            return None, res_name
                return existing_item, None
            else:
                res_name = generate_res_name(item, suffix, index)
                index += 1


def generate_res_name(item: Union[sly.ObjClass, sly.TagMeta], suffix: str, index: int) -> str:
    """Generates a new name for the item.

    :param item: Item to generate a new name for.
    :type item: Union[sly.ObjClass, sly.TagMeta]
    :param suffix: Suffix to add to the name.
    :type suffix: str
    :param index: Index to add to the name.
    :type index: int
    :return: New name for the item.
    :rtype: str
    """
    return f"{item.name}-{suffix}" if index == 0 else f"{item.name}-{suffix}-{index}"
