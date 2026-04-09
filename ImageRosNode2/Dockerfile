FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    gnupg \
    lsb-release \
    ca-certificates

# ROS2 key + repo
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=arm64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu jammy main" \
> /etc/apt/sources.list.d/ros2.list

RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    ros-humble-sensor-msgs

ENV ROS_DISTRO=humble
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

# ----------------------------------------------------
# 📂 6. 放入資料
# ----------------------------------------------------
WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 main.py"]