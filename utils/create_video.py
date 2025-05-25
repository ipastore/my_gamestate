import cv2
import os
import glob
from tqdm import tqdm  # For progress bar

# Path to image directory
img_dir = '/home/student/headers-tracking/headers-gamestate/data/SoccerNetGS/valid/SNGS-021/img1'

# Get all image files and sort them
img_files = sorted(glob.glob(os.path.join(img_dir, '*.jpg')))

if not img_files:
    print(f"No images found in {img_dir}")
    exit(1)

# Read first image to get dimensions
first_img = cv2.imread(img_files[0])
height, width, layers = first_img.shape

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_path = 'SNGS-021_video.mp4'
out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

# Write frames to video
print(f"Creating video from {len(img_files)} frames...")
for img_file in tqdm(img_files):
    img = cv2.imread(img_file)
    out.write(img)

# Release the VideoWriter
out.release()
print(f"Video saved to {output_path}")