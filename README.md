cat << 'EOF' > README.md
# Night-Masked ORB-SLAM3

**A Robust Visual SLAM System for Low-Light Environments**

This repository contains a modified version of **ORB-SLAM3**, optimized for operation in night-time and adverse lighting conditions. It implements a **Glare Masking** preprocessing pipeline to reject unreliable features caused by streetlights and reflections, significantly reducing trajectory drift compared to the standard baseline.

## ⚙️ System Requirements
* **OS:** Ubuntu 22.04 (Jammy Jellyfish)
* **Compiler:** GCC 11 (C++14 standard required)
* **ROS Compatibility:** ROS 2 Humble (Safe to install alongside)

---

## 🛠️ Installation Guide (Safe Mode)

Standard ORB-SLAM3 installation often conflicts with ROS 2 on Ubuntu 22.04 due to dependency mismatches (OpenCV 4 vs. OpenCV 3). 

**We use a "Local Installation" method.** All dependencies (OpenCV 4.6.0, Pangolin) are installed into a local folder (`~/MinKyu/install`) to ensure isolation and system stability.

### 1. Setup Workspace
Create a dedicated workspace to keep dependencies isolated.

\`\`\`bash
# Create directory structure
mkdir -p ~/MinKyu/install
mkdir -p ~/MinKyu/src

# Set environment variables for the build process
export MINKYU_ROOT=~/MinKyu
export INSTALL_DIR=$MINKYU_ROOT/install
\`\`\`

### 2. Install System Tools
Install basic compilation tools and Python dependencies.

\`\`\`bash
sudo apt update
sudo apt install -y build-essential cmake git pkg-config \
    libavcodec-dev libavformat-dev libswscale-dev \
    python3-dev python3-numpy libtbb2 libtbb-dev libjpeg-dev \
    libpng-dev libtiff-dev libglew-dev libboost-all-dev \
    libssl-dev libeigen3-dev libgtk2.0-dev
\`\`\`

### 3. Install OpenCV 4.6.0 (Locally)
We build OpenCV from source to ensure C++ headers are available (which \`pip install\` does not provide).

\`\`\`bash
cd $MINKYU_ROOT/src
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 4.6.0
mkdir build && cd build

# Configure CMake to install to ~/MinKyu/install
cmake -D CMAKE_BUILD_TYPE=Release \
      -D WITH_CUDA=OFF \
      -D CMAKE_INSTALL_PREFIX=$INSTALL_DIR \
      ..

make -j4
make install
\`\`\`

### 4. Install Pangolin (Locally)
**Note:** Python bindings are disabled to prevent build errors with Python 3.12 on Ubuntu 22.04.

\`\`\`bash
cd $MINKYU_ROOT/src
git clone https://github.com/stevenlovegrove/Pangolin.git
cd Pangolin
mkdir build && cd build

# Configure CMake to install to ~/MinKyu/install
cmake .. \
    -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=$INSTALL_DIR \
    -D BUILD_PANGOLIN_PYTHON=OFF

make -j4
make install
\`\`\`

### 5. Build Night-Masked ORB-SLAM3
Clone this repository and compile it, linking against the local dependencies we just created.

\`\`\`bash
cd $MINKYU_ROOT
git clone https://github.com/minq02/NightMaskedORBSLAM3.git
cd NightMaskedORBSLAM3

# Critical: Tell CMake where to find our local OpenCV and Pangolin
export CMAKE_PREFIX_PATH=$INSTALL_DIR:$CMAKE_PREFIX_PATH
export LD_LIBRARY_PATH=$INSTALL_DIR/lib:$LD_LIBRARY_PATH

# Critical: Patch for Ubuntu 22.04 (GCC 11 requires C++14)
# (This repo already includes this fix, but good to double-check)
sed -i 's/++11/++14/g' CMakeLists.txt

# Compile
./build.sh
\`\`\`

---

## 🏃 How to Run

Because libraries are installed in a custom folder, you must tell the terminal where to find them **every time you open a new terminal**.

### 1. Export Library Path
\`\`\`bash
export LD_LIBRARY_PATH=~/MinKyu/install/lib:$LD_LIBRARY_PATH
\`\`\`

### 2. Enable Display (For Shared/Remote Machines)
If the GUI window crashes immediately, run this command to allow the terminal to access the display:
\`\`\`bash
xhost +
\`\`\`

### 3. Run Monocular SLAM (EuRoC Example)
\`\`\`bash
./Examples/Monocular/mono_euroc \
    ./Vocabulary/ORBvoc.txt \
    ./Examples/Monocular/EuRoC.yaml \
    PATH_TO_YOUR_DATASET_FOLDER \
    ./Examples/Monocular/EuRoC_TimeStamps/MH01.txt
\`\`\`

---

## ⚠️ Troubleshooting

**1. "error while loading shared libraries: libpango_windowing.so"**
* **Cause:** Linux doesn't know where the custom libraries are.
* **Fix:** Run \`export LD_LIBRARY_PATH=~/MinKyu/install/lib:$LD_LIBRARY_PATH\`

**2. "Pangolin X11: Failed to open X display"**
* **Cause:** Security permissions blocking the window.
* **Fix:** Run \`xhost +\` before starting the program.

**3. "Segment Fault (core dumped)" immediately**
* **Cause:** Often caused by incorrect path to the Vocabulary file.
* **Fix:** Ensure \`./Vocabulary/ORBvoc.txt\` exists and is extracted (not \`.tar.gz\`).
EOF