from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy import VideoFileClip, AudioFileClip
import os

class colors:
    RED = '\033[31m'
    ENDC = '\033[0m'

def Main():
    # Asking user input for a url
    url = input(f"{colors.RED}Type in the url of which video you'd like to download: {colors.ENDC}")

    # Setting parameters
    yt = YouTube(url=url)
    title = yt.title
    print("Found a video titled: ", title)

    # Change the path where you want to download the video.
    library_path = input(f"{colors.RED}Type the exact location where you want to store your video: {colors.ENDC}")

    # Setting temporary file locations
    videofile_name = library_path+"/TEMP_video.mp4"
    audiofile_name = library_path+"/TEMP_audio.m4a"

    return Downloader(yt, library_path, title, audiofile_name, videofile_name)

def Downloader(yt, library_path, title, audiofile_name, videofile_name):
    print("Video download is starting, this might take a while depending on the video length & quality...")

    # Specifiying the download parameters for pytubefix
    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('bitrate').desc().first()
    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

    # Specifiying download names and paths
    video_stream.download(filename="TEMP_video.mp4", output_path=library_path)
    audio_stream.download(filename="TEMP_audio.m4a", output_path=library_path)

    print("The video download has finished.")

    # A while statement for asking user an input. If not correct, return to where this asks for user input
    valid_input = False
    while not valid_input:
        encoder_of_choice = input(f"{colors.RED}Next, please specify whether you want to use NVENC (GPU), libx264 (CPU) or rawfile encoder. Results may vary depending on which you choose: {colors.ENDC}")
        
        # GPU encoding
        if encoder_of_choice == "NVENC" or encoder_of_choice == "nvenc" or encoder_of_choice == "GPU" or encoder_of_choice == "gpu" or encoder_of_choice == "nvidia":
            ConverterNVENC(library_path, title, audiofile_name, videofile_name)
            valid_input = True
        
        # CPU encoding
        elif encoder_of_choice == "LIBX264" or encoder_of_choice == "libx264" or encoder_of_choice == "CPU" or encoder_of_choice == "cpu":
            ConverterLIBX264(library_path, title, audiofile_name, videofile_name)
            valid_input = True
        
        # Rawfile encofing
        elif encoder_of_choice == "rawfile" or encoder_of_choice == "raw":
            ConverterRaw(library_path, title, audiofile_name, videofile_name)
            valid_input = True
        
        # Invalid input
        else:
            print("Couldn't understand your choice, please retype your choice")

def ConverterLIBX264(library_path, title, audiofile_name, videofile_name):
    print("Video encoding process starting...")

    # Setting video & audio clips for encoding
    video_clip = VideoFileClip(library_path + "/" + "TEMP_video.mp4")
    audio_clip = AudioFileClip(library_path + "/" + "TEMP_audio.m4a")

    # Outcome clip
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(library_path+"/"+title+".mp4", codec='libx264', threads=24)

    # Removing excess files
    print("Cleaning up the working folders...")
    os.remove(audiofile_name)
    os.remove(videofile_name)
    print("Done, enjoy your video :)")

def ConverterNVENC(library_path, title, audiofile_name, videofile_name):
    print("Video encoding process starting...")

    # Setting video & audio clips for encoding
    video_clip = VideoFileClip(library_path + "/" + "TEMP_video.mp4")
    audio_clip = AudioFileClip(library_path + "/" + "TEMP_audio.m4a")

    # Outcome clip
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(library_path+"/"+title+".mp4", codec='hevc_nvenc', threads=32)

    # Removing excess files
    print("Cleaning up the working folders...")
    os.remove(audiofile_name)
    os.remove(videofile_name)
    print("Done, enjoy your video :)")

def ConverterRaw(library_path, title, audiofile_name, videofile_name):
    print("Video encoding process starting...")

    # Setting video & audio clips for encoding
    video_clip = VideoFileClip(library_path + "/" + "TEMP_video.mp4")
    audio_clip = AudioFileClip(library_path + "/" + "TEMP_audio.m4a")

    # Outcome clip
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(library_path+"/"+title+".avi", codec='png', threads=24)

    # Removing excess files
    print("Cleaning up the working folders...")
    os.remove(audiofile_name)
    os.remove(videofile_name)
    print("Done, enjoy your video :)")

Main()