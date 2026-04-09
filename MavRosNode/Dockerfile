FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 🔴 修復 apt sources（關鍵）
RUN rm -f /etc/apt/sources.list && \
    echo "deb http://ports.ubuntu.com/ubuntu-ports jammy main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://ports.ubuntu.com/ubuntu-ports jammy-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://ports.ubuntu.com/ubuntu-ports jammy-security main restricted universe multiverse" >> /etc/apt/sources.list

# 更新 + 基本工具
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    software-properties-common

# ROS2 key
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

# ROS2 repo
RUN echo "deb [arch=arm64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu \
jammy main" \
> /etc/apt/sources.list.d/ros2.list

# 安裝 ROS2 + MAVROS
RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    ros-humble-mavros \
    ros-humble-mavros-extras \
    ros-humble-ros2cli \
    geographiclib-tools

# debug tool
RUN apt update && apt install -y tcpdump \
    net-tools

# MAVROS 必要
RUN geographiclib-get-geoids egm96-5

# ROS 
ENV ROS_DISTRO=humble
ENV ROS_ROOT=/opt/ros/humble
ENV PATH=$ROS_ROOT/bin:$PATH
ENV LD_LIBRARY_PATH=$ROS_ROOT/lib:$LD_LIBRARY_PATH

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

CMD ["bash"]
