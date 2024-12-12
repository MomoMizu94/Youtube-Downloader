from pytubefix import YouTube
import ffmpeg
import os
import requests
from pathlib import Path
import sys

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

    # Setting parameters
    yt = YouTube(url)
    title = yt.title
    '''
    try:
        check_url = requests.get(url, timeout = 3)
    except requests.exceptions.RequestException as e:
        print(f"{colors.RED}Video url was not found. Make sure you have a valid url.{colors.ENDC}")
        sys.exit(1)'''

    print(f"{colors.GREEN}Found a video titled: {title}")

    # User-defined download path
    library_path = input(f"{colors.RED}Type the exact location where you want to store your video: {colors.ENDC}")
    # library_path = "/home/momomizu/Videos"

    # Setting temporary file names
    video_file = Path(library_path) / "TEMP_video.mp4"
    audio_file = Path(library_path) / "TEMP_audio.aac"

    return Downloader(yt, library_path, title, audio_file, video_file)

def Downloader(yt, library_path, title, audio_file, video_file):
    print(f"{colors.GREEN}Video download is starting...{colors.ENDC}")

    # Download video & audio streams
    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('bitrate').desc().first()
    audio_stream = yt.streams.filter(adaptive=True, only_audio=True).order_by('abr').desc().first()

    if audio_stream is None:
        print(f"{colors.RED}No suitable audio stream found, attempting different formats...{colors.ENDC}")

        # Try a different filter, for example, looking for `m4a` or `webm` formats
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True, file_extension='m4a').first()

        if audio_stream is None:
            audio_stream = yt.streams.filter(adaptive=True, only_audio=True, file_extension='webm').first()

    # If still no audio stream found
    if audio_stream is None:
        print(f'{colors.RED}Error: No audio stream found.{colors.ENDC}')
        return  # Exit the function or handle the error appropriately

    # Download video and audio
    print(f"{colors.GREEN}Downloading video and audio...")
    video_stream.download(output_path=library_path, filename="TEMP_video.mp4")
    audio_stream.download(output_path=library_path, filename="TEMP_audio.aac")

    print(f"{colors.GREEN}Download complete.")

    # Prompt user for encoding choice
    encoder_choice = GetEncoderOfChoice()

    if encoder_choice in ['NVENC', 'nvenc', 'GPU', 'gpu']:
        ConverterNVENC(library_path, title, audio_file, video_file)
    
    elif encoder_choice in ['libx264', 'LIBX264', 'CPU', 'cpu']:
        ConverterLIBX264(library_path, title, audio_file, video_file)
    
    elif encoder_choice in ['raw', 'rawfile', 'RAW', 'RAWFILE']:
        ConverterRaw(library_path, title, audio_file, video_file)
    
    else:
        print(f"{colors.RED}Invalid choice. Please try again.{colors.ENDC}")
        return Downloader(yt, library_path, title, audio_file, video_file)

def GetEncoderOfChoice():
    """Prompt user for encoding choice."""
    while True:
        encoder_choice = input(f"{colors.RED}Please choose an encoder (NVENC (GPU), libx264 (CPU), rawfile): {colors.ENDC}")
        if encoder_choice in ['NVENC', 'nvenc', 'GPU', 'gpu', 'libx264', 'LIBX264', 'CPU', 'cpu', 'rawfile', 'raw', 'RAW', 'RAWFILE']:
            return encoder_choice
        print(f"{colors.RED}Invalid input. Please choose again.{colors.ENDC}")

# Jatka värien lisäilyä!!!! + Parempi väri vihreän sijaan??
def ConverterLIBX264(library_path, title, audio_file, video_file):
    print("Encoding video using libx264...")

    output_path = Path(library_path) / f"{title}.mp4"

    # Convert Path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # FFmpeg command for libx264
    (
        ffmpeg
        .concat(ffmpeg.input(video_file_str), ffmpeg.input(audio_file_str), v=1, a=1)
        .output(str(output_path), vcodec='libx264', acodec='aac', threads=16, preset='medium', \
        crf=10, movflags='faststart', loglevel='quiet')
        .run()
    )

    print(f"Video encoding complete: {output_path}")
    CleanUp(audio_file, video_file)

def ConverterNVENC(library_path, title, audio_file, video_file):
    print("Encoding video using Nvenc...")

    output_path = Path(library_path) / f"{title}.mp4"

    # Convert Path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # FFmpeg command for Nvenc (gpu)
    (
        ffmpeg
        .concat(ffmpeg.input(video_file_str), ffmpeg.input(audio_file_str), v=1, a=1)
        .output(library_path+"/"+title+".mp4", vcodec='hevc_nvenc', acodec='aac', preset='fast', crf=0, \
        movflags='faststart', loglevel='quiet')
        .run()
    )

    print(f"Video encoding complete: {output_path}")
    CleanUp(audio_file, video_file)


def ConverterRaw(library_path, title, audio_file, video_file):
    print("Encoding video using png...")

    # Convert Path objects to string objects before passing to ffmpeg
    video_file_str = str(video_file)
    audio_file_str = str(audio_file)

    # FFmpeg command for Nvenc (gpu)
    (
        ffmpeg
        .concat(ffmpeg.input(video_file_str), ffmpeg.input(audio_file_str), v=1, a=1)
        .output(library_path+"/"+title+".avi", vcodec='png', acodec='aac', threads=16, preset='veryslow', \
        crf=0, movflags='faststart', loglevel='quiet')
        .run()
    )

    print(f"Video encoding complete: {output_path}")
    CleanUp(audio_file, video_file)

def CleanUp(video_file, audio_file):
    """Remove temporary files after encoding."""
    os.remove(audio_file)
    os.remove(video_file)
    print("Cleaned up temporary files.")

if __name__ == '__main__':
    Main()

# TODO:
# Lisää paremmat error viestit eri kohtiin. esim joissa kysytään user inputtia.
# Kokeile buildaa ffmpeg viel uusiks tarvittavil moduuleil, jos ton hvencin sais toimii paremmal laadul
# Tee executable täst
