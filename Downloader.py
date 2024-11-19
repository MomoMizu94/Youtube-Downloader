from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy.editor import VideoFileClip, AudioFileClip
#rom moviepy.config import change_settings
import os

# Asking user input for a url
url = input("Type in the url of which video you'd like to download: ")

# Setting parameters
yt = YouTube(url=url)
title = yt.title
print("Found a video titled: ", title)

# Change the path where you want to download the video.
library_path = "/home/momomizu/Videos"
print("The location for the video will be: ", library_path)

# Setting temporary file locations
videofile_name = library_path+"/TEMP_video.mp4"
audiofile_name = library_path+"/TEMP_audio.m4a"

#change_settings({"FFMPEG_BINARY":"ffmpeg"})

def Downloader():
    print("Video download is starting, this might take a while depending on the video length...")

    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('bitrate').desc().first()
    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
    
    #video_stream.download(output_path=library_path)
    #audio_stream.download(output_path=library_path)

    video_stream.download(filename="TEMP_video.mp4", output_path=library_path)
    audio_stream.download(filename="TEMP_audio.m4a", output_path=library_path)

def Converter():
    print("Video encoding process starting...")
    #video_clip = VideoFileClip(videofile_name)
    #audio_clip = AudioFileClip(audiofile_name)

    video_clip = VideoFileClip(library_path + "/" + "TEMP_video.mp4")
    audio_clip = AudioFileClip(library_path + "/" + "TEMP_audio.m4a")

    #print(video_clip)
    #print(audio_clip)

    final_clip = video_clip.set_audio(audio_clip)
    #final_clip.write_videofile(library_path+"/"+title+".mp4", codec='h264_nvenc')
    #final_clip.write_videofile(library_path+"/"+title+".avi", codec='png', threads=24)
    final_clip.write_videofile(library_path+"/"+title+".mp4", codec='libx264', threads=24)

    print("Cleaning up the working folders...")
    os.remove(audiofile_name)
    os.remove(videofile_name)
    print("Done, enjoy your video :)")

Downloader()
Converter()