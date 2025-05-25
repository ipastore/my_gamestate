import streamlit as st
import subprocess
import os
import time
import shutil
from datetime import datetime
import tempfile
import time
from utils.video_processing import convert_to_h264_aac, is_valid_video, get_latest_output_video, convert_to_youtube_short_url

# Set page configuration
st.set_page_config(
    page_title="SoccerNet GameState Processor",
    page_icon="⚽",
    layout="wide"
)

# Constants
ROOT_DIR = f"/home/student/headers-tracking/my_gamestate"
CONFIG_DIR = f"{ROOT_DIR}/configs"
OUTPUT_DIR = f"{ROOT_DIR}/outputs/sn-gamestate"
UPLOADS_DIR = f"{ROOT_DIR}/uploads"  # Directory for uploaded videos

# Create uploads directory if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_tracklab_command(video_path):
    """Run the tracklab command with the specified video path in a separate terminal and wait for it to finish before returning."""
    # Prepare the command string
    command_str = f"cd {ROOT_DIR} && tracklab --config-dir=\"{CONFIG_DIR}\" -cn my_soccernet dataset=\"youtube\" dataset.eval_set=\"val\" dataset.video_path=\"{video_path}\""
    
    # Create a script file to execute in the terminal
    script_path = "/tmp/run_tracklab.sh"
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"{command_str}\n")
        #touch /tmp/tracklab_done.signal
        f.write("touch /tmp/tracklab_done.signal\n")
        f.write("echo 'Process completed. You can close this terminal.'\n")
        f.write("read -p 'Press Enter to close this terminal...'\n")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    # Find an available terminal emulator
    terminal_emulators = [
        ["gnome-terminal", "--", "bash", script_path],
        ["xterm", "-e", "bash", script_path],
        ["konsole", "-e", "bash", script_path],
        ["terminator", "-e", "bash", script_path]
    ]
    terminal_cmd = None
    for emulator in terminal_emulators:
        if shutil.which(emulator[0]):
            terminal_cmd = emulator
            break
    
    if not terminal_cmd:
        st.error("Could not find a terminal emulator. Please run the command manually in your terminal.")
        st.code(command_str, language="bash")
        return 1
    try:
        st.info("TrackLab is running in a separate terminal window. Please wait until you close the terminal window (after pressing Enter) before the app continues.")
        with st.spinner("Processing video with SoccerNet GameState pipeline... (waiting for terminal to close)"):
            signal_file = "/tmp/tracklab_done.signal"
            # Remove any old signal file before starting
            if os.path.exists(signal_file):
                os.remove(signal_file)
            terminal_process = subprocess.Popen(terminal_cmd)
            terminal_process.wait()

            # Wait for the signal file to appear
            timeout = 60 * 60  # 1 hour max
            start_time = time.time()
            while not os.path.exists(signal_file):
                if time.time() - start_time > timeout:
                    st.error("Processing timed out.")
                    return 1
                time.sleep(2)  # check every 2 seconds

            #Remove the signal file after detecting it
            os.remove(signal_file)
    
        return_code = terminal_process.returncode if terminal_process.returncode is not None else 1
    except Exception as e:
        st.error(f"Error running TrackLab: {str(e)}")
        st.info("As a fallback, you can run this command manually in your terminal:")
        st.code(command_str, language="bash")
        return_code = 1
    finally:
        if return_code == 0:
            st.success("Processing completed successfully!")
        else:
            st.error(f"Processing failed with return code: {return_code}")
    return return_code


def main():
    """Main function for the Streamlit app."""
    st.title("⚽ SoccerNet GameState Processor")
    st.write("Upload a football video or provide a YouTube URL to process with SoccerNet GameState pipeline.")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["Local Video Upload", "YouTube URL"])
    
    # Variables to store the video path and type
    video_path = None
    
    # Tab 1: Local video upload
    with tab1:
        uploaded_file = st.file_uploader("Upload a video file (.mp4, .avi, etc.)", 
                                         type=["mp4", "avi", "mov", "mkv"])
        
        if uploaded_file is not None:
            # Create a filename with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(UPLOADS_DIR, filename)
            
            # Save the uploaded file to our uploads directory
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            video_path = file_path
            
            # Convert to browser-compatible format
            converted_path = file_path.rsplit('.', 1)[0] + "_browser.mp4"
            
            with st.spinner("Converting video to browser-compatible format... Please wait a moment ⏳"):
                if convert_to_h264_aac(video_path, converted_path):
                    video_path = converted_path  # Use the converted file for display
                    
            st.video(video_path)
            st.write(f"Video saved at: {video_path}")
    
    # Tab 2: YouTube URL
    with tab2:
        youtube_url = st.text_input("Enter a YouTube video URL")
        shortened_url = convert_to_youtube_short_url(youtube_url)

        if youtube_url:
            video_path = shortened_url
            
            # Display the YouTube video
            st.video(shortened_url)
    
    # Processing section
    st.markdown("---")
    st.subheader("Video Processing")
    
    # Process button
    if video_path and st.button("Process Tracking"):
        # Run the tracklab command in a separate terminal
        return_code = run_tracklab_command(video_path)
        
        # If processing was successful, find and display the output video
        if return_code == 0:
            # Find the latest output video
            output_video = get_latest_output_video(OUTPUT_DIR)
            
            if output_video:
                st.markdown("---")
                st.subheader("Processed Video Output")
                try:
                    # Create a temporary directory for browser-compatible videos if it doesn't exist
                    if not hasattr(st.session_state, 'temp_dir'):
                        st.session_state.temp_dir = tempfile.TemporaryDirectory()
                    
                    # Convert the output video to browser-compatible format in the temp directory
                    temp_filename = f"output_browser_{int(time.time())}.mp4"
                    converted_output_path = os.path.join(st.session_state.temp_dir.name, temp_filename)
                    
                    convert_to_h264_aac(output_video, converted_output_path)
                    
                    # Display the processed video
                    st.video(converted_output_path)
                    st.write(f"After processing, the output video is saved at: {output_video}")
                    
                except Exception as e:
                    st.error(f"Error displaying processed video: {e}")
                    st.write(f"The video was processed successfully but cannot be displayed in the browser.")
                    
            else:
                st.warning("No output video found after processing.")
                st.write("This could mean the processing is still ongoing or encountered an error.")
                st.write("Check the terminal window where the processing is running for more details.")
    

    # Information section
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    This app uses the SoccerNet GameState pipeline to process football videos.
    The pipeline runs tracking algorithms to track players and the ball, and
    visualizes the results.
    
    **Note:** Processing may take several minutes depending on the video length.
    """)


if __name__ == "__main__":
    main()
