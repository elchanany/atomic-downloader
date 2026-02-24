import os
import zipfile
import urllib.request
import shutil

FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
ZIP_NAME = "ffmpeg.zip"
EXTRACT_DIR = "ffmpeg_temp"

def download_ffmpeg():
    print("Downloading FFmpeg...")
    urllib.request.urlretrieve(FFMPEG_URL, ZIP_NAME)
    print("Download complete. Extracting...")
    
    with zipfile.ZipFile(ZIP_NAME, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
        
    print("Extraction complete. Moving binaries...")
    
    # Find bin folder
    bin_dir = None
    for root, dirs, files in os.walk(EXTRACT_DIR):
        if 'bin' in dirs:
            bin_dir = os.path.join(root, 'bin')
            break
            
    if bin_dir:
        for file in ['ffmpeg.exe', 'ffprobe.exe']:
            src = os.path.join(bin_dir, file)
            if os.path.exists(src):
                shutil.move(src, file)
                print(f"Moved {file}")
    
    # Cleanup
    print("Cleaning up...")
    os.remove(ZIP_NAME)
    shutil.rmtree(EXTRACT_DIR)
    print("FFmpeg installed successfully!")

if __name__ == "__main__":
    download_ffmpeg()
