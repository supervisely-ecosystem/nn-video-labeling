<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.2/poster1.png"/>

# Apply NN to Video Frames

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Demo">Demo</a> •
  <a href="#Related-Apps">Related Apps</a> •
  <a href="#How-To-Run">How To Run</a> •
    <a href="#Screenshot">Screenshot</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/nn-video-labeling/annotation-tool)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/nn-video-labeling)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/nn-video-labeling.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/nn-video-labeling.png)](https://supervise.ly)

</div>

# Overview

Any NN can be integrated into the Video Labeling interface if it has a properly implemented serving app (for example: Serve YOLOv8). The app adds classes and tags to the project automatically.

The application allows you to apply a served neural network to a single frame of the video.

Application key points:

- Connects to Served models in Supervisely
- Supports Object Detection Models
- Supports Instance Segmentation Models
- Supports Semantic Segmentation Models
- Does not support tracking (creates new objects for each frame)

# Related Apps

The application supports the following models:

### Object Detection:

- [Serve YOLOv8](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/yolov8/serve)  
   <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/yolov8/serve" src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/yoloV8.png" width="350px"/>
- [Serve MMDetection 3.0](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/serve-mmdetection-v3)  
  <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/serve-mmdetection-v3" src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/mmDet3.png" width="350px"/>

### Instance Segmentation:

- [Serve Detectron2](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/detectron2/supervisely/instance_segmentation/serve)  
   <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/detectron2/supervisely/instance_segmentation/serve" src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/detectron2.png" width="350px"/>
- [Serve YOLOv8](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/yolov8/serve)  
   <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/yolov8/serve" src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/yoloV8.png" width="350px"/>
- [Serve MMDetection 3.0](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/serve-mmdetection-v3)  
   <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/serve-mmdetection-v3" src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/mmDet3.png" width="350px"/>


# How to Run

1. Launch Serve APP, designed for Videos Projects

<img src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/deploy_nn.png" width="80%" style='padding-top: 10px'>

2. Run [Apply NN to Video Frames](https://ecosystem.supervise.ly/apps/nn-video-labeling) in the Video Labeling interface:

<img src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/runnn.png" width="80%" style='padding-top: 10px'>

3. Set the settings and apply NN to the current video frame

# Screenshot

<img src="https://github.com/supervisely-ecosystem/nn-video-labeling/releases/download/v0.0.1/applynn.png" width="80%" style='padding-top: 10px'>
