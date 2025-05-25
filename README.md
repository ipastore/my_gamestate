# SoccerNet GameState Project

A Streamlit web application for running the SoccerNet sn-gamestate pipeline on user-provided football videos. This project extends and benchmarks the [SoccerNet GameState Reconstruction](https://github.com/SoccerNet/sn-gamestate) and [TrackLab](https://github.com/TrackingLaboratory/tracklab) frameworks.

## Project Structure

All three repositories should be cloned as sibling folders in the same parent directory:

```
headers-tracking/
├── my_gamestate/   # This repo (custom code, scripts, Streamlit app)
├── headers-gamestate/   # Fork of sn-gamestate
└── headers-tracklab/    # Fork of tracklab
```

## Step-by-Step Setup

### 1. Clone All Three Repositories

```bash
# Create the parent directory
mkdir -p headers-tracking
cd headers-tracking

# Clone your forks
git clone https://github.com/ipastore/my_gamestate.git
git clone https://github.com/ipastore/headers-tracklab.git
git clone https://github.com/ipastore/headers-gamestate.git
```

### 2. Create and Activate the Conda Environment

```bash
# Create a new conda environment
conda create -n tracklab python=3.9 pip -y
conda activate tracklab
```

### 3. Install Project Dependencies

```bash
# Install dependencies for headers-tracklab
cd headers-tracklab
pip install -e .


# Install additional dependencies
pip install openmim==0.3.9          # Needed for mmcv
mim install mmcv==2.0.1

# Install Streamlit for the web app
pip install streamlit
```

## Running the Streamlit App

1. Make sure you have the `tracklab` conda environment activated:
   ```bash
   conda activate tracklab
   ```

2. Run the Streamlit app from the correct directory:
   ```bash
   cd /home/student/headers-tracking/my_gamestate
   streamlit run streamlit_app.py
   ```

   Alternatively, use the provided script:
   ```bash
   ./run_app.sh
   ```

3. Open your browser to the URL shown in the terminal (typically http://localhost:8501)

## Usage

1. Upload a video file or paste a YouTube URL
2. Click "Process Tracking" to run the SoccerNet GameState pipeline
3. View the processed video when it completes


## Directory Structure

- `streamlit_app.py`: Main Streamlit application
- `run_app.sh`: Convenience script for running the app
- `configs/`: Custom configuration files for the pipeline
- `uploads/`: Directory for video uploads
- `outputs/`: Directory for pipeline outputs
- `utils/`: Utility scripts for video processing
- `yolov11/`: YOLOv11 training and inference files

## Technical Details

The application uses:
- **Streamlit**: For the web interface
- **TrackLab**: For tracking player movements
- **SoccerNet GameState**: For team assignment and game state reconstruction

