#!/bin/bash
# This script runs the Streamlit app with the correct environment

cd /home/student/headers-tracking/my_gamestate
source ~/anaconda3/etc/profile.d/conda.sh
conda activate tracklab
streamlit run streamlit_app.py
