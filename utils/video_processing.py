def convert_to_youtube_short_url(url):
    """Convert any YouTube URL to the short youtu.be format."""
    import re
    
    # Regular expression to extract video ID
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\?\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://youtu.be/{video_id}"
    
    # Return original if no match found
    return url


def convert_to_h264_aac(input_path, output_path):
    import subprocess
    """
    Convert a video to H.264 video and AAC audio for browser compatibility.
    Returns True if successful, False otherwise.
    """
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

# Function to check if a video file is valid
def is_valid_video(file_path):
    import os
    import shutil
    import subprocess

    """Check if a file is a valid video that can be played."""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not os.access(file_path, os.R_OK):
        return False, "File is not readable"
    
    # Check file size
    if os.path.getsize(file_path) == 0:
        return False, "File is empty"
    
    # Try to get video info using ffprobe (if available)
    try:
        if shutil.which('ffprobe'):
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                   'format=duration', '-of', 
                   'default=noprint_wrappers=1:nokey=1', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"Not a valid video file: {result.stderr}"
            return True, "Valid video file"
    except Exception as e:
        pass
    
    # If ffprobe is not available, just check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    if any(file_path.lower().endswith(ext) for ext in valid_extensions):
        return True, "File has valid extension"
    
    return False, "File does not have a valid video extension"


def get_latest_output_video(output_dir):
    import os
    import glob
    import streamlit as st
    import tempfile

    """Find the most recently created output video from the pipeline."""
    # Get all dates directories
    date_dirs = sorted(glob.glob(f"{output_dir}/*"))
    if not date_dirs:
        st.write("No date directories found in output path.")
        st.write(f"Output directory: {output_dir}")
        st.write(f"Output directory exists: {os.path.exists(output_dir)}")
        return None
    
    latest_date_dir = date_dirs[-1]
    
    # Get all time directories within the latest date
    time_dirs = sorted(glob.glob(f"{latest_date_dir}/*"))
    if not time_dirs:
        st.write(f"No time directories found in latest date directory: {latest_date_dir}")
        return None
    
    latest_time_dir = time_dirs[-1]
    
    # Look for videos in the visualization directory
    video_dir = f"{latest_time_dir}/visualization/videos"
    
    # Check if directory exists
    if not os.path.exists(video_dir):
        st.write(f"Visualization directory not found: {video_dir}")
        return None
    
    videos = glob.glob(f"{video_dir}/*.mp4")

    if not videos:
        return None
    
    # Ensure we're returning an absolute path
    video_path = os.path.abspath(videos[0])

    return video_path
