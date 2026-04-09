#!/bin/bash
set -e

source /opt/ros/humble/setup.bash

echo "=== START v4l2_camera ==="

ros2 run v4l2_camera v4l2_camera_node \
  --ros-args \
  -p video_device:=/dev/video0 \
  -p image_size:="[1280,720]" \
  -p pixel_format:=UYVY