# ======================================================
# 🧩 Base
# ======================================================
FROM ultralytics/ultralytics:latest-jetson-jetpack6@sha256:dee7b672e7ef818c508acc241368d7e27cb75f2cf6b2986c3cae871506adaf9b

# ======================================================
# 基本工具
# ======================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-gi \
    gir1.2-gstreamer-1.0 \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-gl \
    iproute2 \
    iputils-ping \
 && rm -rf /var/lib/apt/lists/*


# ----------------------------------------------------
# 📂 6. 放入資料
# ----------------------------------------------------
WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]