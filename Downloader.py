import yt_dlp
import os
import requests
import subprocess
from tqdm import tqdm
from pathlib import Path
import sys
import platform


class colors:

    RED = '\033[31m'
    ENDC = '\033[0m'
    GREEN  = '\033[32m'
    BLUE   = "\033[34m"
    PURPLE = "\033[35m"
    CYAN   = "\033[36m"
    WHITE  = "\033[37m"
    YELLOW = "\033[33m"


def Main():

    # Asking user input for a url
    url = input(f"{colors.RED}Type in the url of which video you'd like to download: {colors.ENDC}")
    
    try:

        # Check if the URL is reachable by sending a request
        check_url = requests.get(url, timeout=3)
        # Raise HTTPError for bad responses
        check_url.raise_for_status()

        # If url is reachable, proceed to load the YouTube video
        with yt_dlp.YoutubeDL({"quiet": True}) as ytdl:
            info = ytdl.extract_info(url, download=False)
            title = info.get("title", "output")
            print(f"{colors.GREEN}Found a video titled: {title}")

    except requests.exceptions.RequestException as e:

        # Handles url related errors
        print(f"{colors.RED}Video URL was not found or is unreachable. Make sure you have a valid URL.{colors.ENDC}")
        sys.exit(1)

    except Exception as e:

        # Handle possible errors when creating the YouTube object
        print(f"{colors.RED}An error occurred while fetching the video: {str(e)}{colors.ENDC}")
        sys.exit(1)

    # Get platform & necessary paths
    library_path, video_file, audio_file = GetPlatformAndOperatingSystem()

    return Downloader(url, title, library_path, audio_file, video_file)


def GetPlatformAndOperatingSystem():

    # For checking the platform and login name
    ### Windows pathing has not been tested ###
    if platform.system() == 'Windows':
        library_path = os.path.join('C:', 'users', os.getlogin(), 'Videos')
    elif platform.system() == 'Linux':
        library_path = os.path.join('/', 'home', os.getlogin(), 'Videos')

    # Creates necessary paths for temp files
    video_file = Path(library_path) / "TEMP_video.mp4"
    audio_file = Path(library_path) / "TEMP_audio.aac"

    return library_path, video_file, audio_file


def Downloader(url, title, library_path, audio_file, video_file):

    print(f"{colors.GREEN}Initiating download...{colors.ENDC}")

    try:

        # Video download
        with yt_dlp.YoutubeDL({
                'format' : 'bv*[ext=mp4]/bv*',  # Fallback to best video if no mp4
                'outtmpl' : str(video_file),
                'noplaylist' : True,
                'quiet': True,
                'no_warnings' : True,
                'merge_output_format' : 'never',
                'postprocessors' : []
            }) as ytdl:
            ytdl.download([url])
            print(f"{colors.GREEN}Video download complete.{colors.ENDC}")

        # Audio download
        with yt_dlp.YoutubeDL({
                'format': 'ba[ext=m4a]/ba',     # Fallback to best audio if no m4a
                'outtmpl': str(audio_file),
                'noplaylist': True,
                'quiet': True,
                'no_warnings' : True,
                'merge_output_format' : 'never',
                'postprocessors' : []
            }) as ytdl:
            ytdl.download([url])
            print(f"{colors.GREEN}Audio download complete.{colors.ENDC}")

    except Exception as e:
        print(f"{colors.RED}Download failed: {str(e)}{colors.ENDC}")
        sys.exit(1)

    # Prompt user for encoding choice
    encoder_choice = GetEncoderOfChoice()

    if encoder_choice in ['NVENC', 'nvenc', 'NVIDIA', 'nvidia', '1']:
        ConverterNvenc(library_path, title, audio_file, video_file)

    if encoder_choice in ['VAAPI', 'vaapi', 'AMD', 'amd', '2']:
        ConverterVaapi(library_path, title, audio_file, video_file)
    
    elif encoder_choice in ['libx265', 'LIBX265', 'CPU', 'cpu', '3']:
        ConverterLibx265(library_path, title, audio_file, video_file)
    
    elif encoder_choice in ['raw', 'rawfile', 'RAW', 'RAWFILE', '4']:
        ConverterRaw(library_path, title, audio_file, video_file)
    
    else:
        print(f"{colors.RED}Invalid choice. Please try again.{colors.ENDC}")
        return Downloader(url, title, library_path, audio_file, video_file)


def GetEncoderOfChoice():

    # Prompt user for encoding choice.
    while True:
        encoder_choice = input(f"{colors.RED}Please choose an encoder:{colors.ENDC}\n 1. Nvenc = Nvidia gpu\n 2. Vaapi = AMD gpu\n 3. Libx265 = cpu\n 4. Rawfile     ")
        if encoder_choice in ['NVENC', 'nvenc', 'NVIDIA', 'nvidia', '1', 'VAAPI', 'vaapi', 'AMD', 'amd', '2', 'libx265', 'LIBX265', 'CPU', 'cpu', '3', 'rawfile', 'raw', 'RAW', 'RAWFILE', '4']:
            return encoder_choice

        print(f"{colors.RED}Invalid input. Please choose again.{colors.ENDC}")


def GetVideoDuration(video_file):

    # Ffprobe to get the video duration
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', video_file
    ]
    
    try:
        # Run the ffprobe command to get the duration in seconds
        duration_str = subprocess.check_output(command).decode().strip()
        total_duration = float(duration_str)  # Convert to float (seconds)
        return total_duration

    except subprocess.CalledProcessError as e:
        # If Ffprobe fails
        print(f"{colors.RED}Error running ffprobe to get video duration: {e.output}{colors.ENDC}")
        raise

    except ValueError:
        # If duration_str can't be converted
        print(f"{colors.RED}Error: Could not convert the duration to float: {duration_str}{colors.ENDC}")
        raise


def ConverterLibx265(library_path, title, audio_file, video_file):

    print(f"{colors.GREEN}Encoding video using libx265...{colors.ENDC}")

    # Sanitizing title to ensure there are no special characters that could cause issues
    safe_title = "".join(x for x in title if x.isalnum() or x.isspace()).replace(" ", "_")
    output_path = Path(library_path) / f"{safe_title}.mp4"

    # Convert Path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # Initialize the ffmpeg command
    command = [
        'ffmpeg',
        '-i', video_file_str,
        '-i', audio_file_str,
        '-c:v', 'libx265',
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-threads', '16',
        '-preset', 'medium',
        '-crf', '10',
        '-movflags', 'faststart',
        '-loglevel', 'info',
        '-y', str(output_path)
    ]

    # Get the total duration of the video file
    total_duration = GetVideoDuration(video_file)

    # Start ffmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Initialize progress bar & formatting
    progress_bar = tqdm(total=100, desc="Encoding Progress", ncols=100, unit='%', \
        bar_format='{desc}: |{bar}|{percentage:3.0f}%', colour='blue', leave=False)

    # Parse stderr for progress information
    for line in process.stderr:
        if 'frame=' in line and 'time=' in line:

            try:
                # Extract time, split it & convert into total seconds
                time_str = line.split('time=')[1].split(' ')[0]
                time_parts = time_str.split(':')

                if len(time_parts) == 3:  # Expected format: hh:mm:ss.xx
                    seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])

                    # Calculate the progress percentage
                    progress = (seconds / total_duration) * 100

                    # Round to 2 decimals places
                    progress = round(progress, 2)
                    
                    # Update to progress bar
                    progress_bar.n = progress
                    progress_bar.last_print_n = progress
                    progress_bar.set_postfix_str(f'{progress}%')
                    progress_bar.update(0)
            
            # If error in parsing time print an error message and continue
            except ValueError:
                print(f"{colors.RED}Error parsing time: {line}{colors.ENDC}")
                continue

    # Wait for the ffmpeg process to finish
    process.wait()

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"{colors.RED}FFmpeg error:{colors.ENDC}\n{stderr}")
    else:
        print(f"\n{colors.GREEN}Video encoding complete. You can find the video here: {output_path}{colors.ENDC}")

    # Clean any left-over files
    CleanUp(audio_file, video_file)


def ConverterNvenc(library_path, title, audio_file, video_file):

    print(f"{colors.GREEN}Encoding video using Nvenc...{colors.ENDC}")

    # Sanitizing title to ensure there are no special characters that could cause issuues
    safe_title = "".join(x for x in title if x.isalnum() or x.isspace()).replace(" ", "_")
    output_path = Path(library_path) / f"{safe_title}.mp4"

    # Convert path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # Initialize the ffmpeg command
    command = [
        'ffmpeg',
        '-i', video_file_str,
        '-i', audio_file_str,
        '-c:v', 'hevc_nvenc',
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-profile:v', 'main10',
        '-preset:v', 'p7',
        '-tune:v', 'uhq',
        '-highbitdepth', '1',
        '-multipass', 'fullres',
        '-rc:v', 'vbr',
        '-b:v', '0',
        '-cq', '28',
        '-qmin', '15',
        '-g', '150',
        '-keyint_min', '15',
        '-rc-lookahead:v', '20',
        '-unidir_b', '1',
        '-tf_level', '4',
        '-preset', 'fast',
        '-bufsize', '20M',
        '-crf', '0',
        '-movflags', 'faststart',
        '-loglevel', 'info',
        '-y', str(output_path)
    ]

    # Get the total duration of the video file
    total_duration = GetVideoDuration(video_file)

    # Start ffmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Initialize progress bar & formatting
    progress_bar = tqdm(total=100, desc="Encoding Progress", ncols=100, unit='%', \
        bar_format='{desc}: |{bar}|{percentage:3.0f}%', colour='blue', leave=False)

    # Parse stderr for progress information
    for line in process.stderr:
        if 'frame=' in line and 'time=' in line:

            try:
                # Extract time, split it & convert into total seconds
                time_str = line.split('time=')[1].split(' ')[0]
                time_parts = time_str.split(':')

                if len(time_parts) == 3:  # Expected format: hh:mm:ss.xx
                    seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])

                    # Calculate the progress percentage
                    progress = (seconds / total_duration) * 100

                    # Round to 2 decimals places
                    progress = round(progress, 2)
                    
                    # Update to progress bar
                    progress_bar.n = progress
                    progress_bar.last_print_n = progress
                    progress_bar.set_postfix_str(f'{progress}%')
                    progress_bar.update(0)
            
            # If error in parsing time print an error message and continue
            except ValueError:
                print(f"{colors.RED}Error parsing time: {line}{colors.ENDC}")
                continue

    # Wait for the ffmpeg process to finish
    process.wait()

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"{colors.RED}FFmpeg error:{colors.ENDC}\n{stderr}")
    else:
        print(f"\n{colors.GREEN}Video encoding complete. You can find the video here: {output_path}{colors.ENDC}")

    # Clean any left-over files
    CleanUp(audio_file, video_file)


def ConverterVaapi(library_path, title, audio_file, video_file):

    print(f"{colors.GREEN}Encoding video using Vaapi...{colors.ENDC}")

    # Sanitizing title to ensure there are no special characters that could cause issuues
    safe_title = "".join(x for x in title if x.isalnum() or x.isspace()).replace(" ", "_")
    output_path = Path(library_path) / f"{safe_title}.mp4"

    # Convert path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # Ffmpeg command
    command = [
        'ffmpeg',
        '-vaapi_device', '/dev/dri/renderD128',
        '-i', video_file_str,
        '-i', audio_file_str,
        '-vf', 'format=nv12,hwupload',
        '-c:v', 'hevc_vaapi',
        '-profile:v', 'main',
        '-global_quality', '20',
        '-g', '150',
        '-keyint_min', '15',
        '-bf', '2',
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', 'faststart',
        '-loglevel', 'info',
        '-y', str(output_path)
    ]

    # Get the total duration of the video file
    total_duration = GetVideoDuration(video_file)

    # Start ffmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Initialize progress bar & formatting
    progress_bar = tqdm(total=100, desc="Encoding Progress", ncols=100, unit='%', \
        bar_format='{desc}: |{bar}|{percentage:3.0f}%', colour='blue', leave=False)

    # Parse stderr for progress information
    for line in process.stderr:
        if 'frame=' in line and 'time=' in line:

            try:
                # Extract time, split it & convert into total seconds
                time_str = line.split('time=')[1].split(' ')[0]
                time_parts = time_str.split(':')

                if len(time_parts) == 3:  # Expected format: hh:mm:ss.xx
                    seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])

                    # Calculate the progress percentage
                    progress = (seconds / total_duration) * 100

                    # Round to 2 decimals places
                    progress = round(progress, 2)
                    
                    # Update to progress bar
                    progress_bar.n = progress
                    progress_bar.last_print_n = progress
                    progress_bar.set_postfix_str(f'{progress}%')
                    progress_bar.update(0)
            
            # If error in parsing time print an error message and continue
            except ValueError:
                print(f"{colors.RED}Error parsing time: {line}{colors.ENDC}")
                continue

    # Wait for the ffmpeg process to finish
    process.wait()

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"{colors.RED}FFmpeg error:{colors.ENDC}\n{stderr}")
    else:
        print(f"\n{colors.GREEN}Video encoding complete. You can find the video here: {output_path}{colors.ENDC}")

    # Clean any left-over files
    CleanUp(audio_file, video_file)


def ConverterRaw(library_path, title, audio_file, video_file):

    print("Encoding video using png...")

    # Sanitizing title to ensure there are no special characters that could cause issues
    safe_title = "".join(x for x in title if x.isalnum() or x.isspace()).replace(" ", "_")
    output_path = Path(library_path) / f"{safe_title}.avi"

    # Convert path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # Initialize the ffmpeg command
    command = [
        'ffmpeg',
        '-i', video_file_str,
        '-i', audio_file_str,
        '-c:v', 'png',
        '-c:a', 'aac',
        '-threads', '16',
        '-preset', 'veryslow',
        '-crf', '0',
        '-movflags', 'faststart',
        '-loglevel', 'info',
        '-y', str(output_path)
    ]

    # Get the total duration of the video file
    total_duration = GetVideoDuration(video_file)

    # Start ffmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Initialize progress bar & formatting
    progress_bar = tqdm(total=100, desc="Encoding Progress", ncols=100, unit='%', \
        bar_format='{desc}: |{bar}|{percentage:3.0f}%', colour='blue', leave=False)

    # Parse stderr for progress information
    for line in process.stderr:
        if 'frame=' in line and 'time=' in line:

            try:
                # Extract time, split it & convert into total seconds
                time_str = line.split('time=')[1].split(' ')[0]
                time_parts = time_str.split(':')

                if len(time_parts) == 3:  # Expected format: hh:mm:ss.xx
                    seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])

                    # Calculate the progress percentage
                    progress = (seconds / total_duration) * 100

                    # Round to 2 decimals places
                    progress = round(progress, 2)
                    
                    # Update to progress bar
                    progress_bar.n = progress
                    progress_bar.last_print_n = progress
                    progress_bar.set_postfix_str(f'{progress}%')
                    progress_bar.update(0)
            
            # If error in parsing time print an error message and continue
            except ValueError:
                print(f"{colors.RED}Error parsing time: {line}{colors.ENDC}")
                continue

    # Wait for the ffmpeg process to finish
    process.wait()

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"{colors.RED}FFmpeg error:{colors.ENDC}\n{stderr}")
    else:
        print(f"\n{colors.GREEN}Video encoding complete. You can find the video here: {output_path}{colors.ENDC}")

    # Clean any left-over files
    CleanUp(audio_file, video_file)


def CleanUp(video_file, audio_file):

    # Remove temporary files after encoding
    os.remove(audio_file)
    os.remove(video_file)
    print("Cleaned up temporary files.")


if __name__ == '__main__':

    Main()