# Installation
1. Install [**python3**](https://www.python.org/downloads/) with **pip** (tested on **python3.11**)
3. Install [**NVIDIA CUDA**](https://developer.nvidia.com/cuda-12-1-1-download-archive) if you have NVIDIA GPU. Make sure your CUDA version is supported by torch
2. Install [**torch**](https://pytorch.org/get-started/locally/) for your CUDA version or for CPU if no NVIDIA GPU is avaliable
4. Install other dependencies:
    ```sh
    pip install -r requirements.txt
    ```
5. Launch
    ```sh
    python main.py
