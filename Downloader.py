from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy.editor import VideoFileClip, AudioFileClip
import os

# Change the url according to the video you want to download
url = "https://www.youtube.com/watch?v=R3GfuzLMPkA"
# Change the path where you want to download the video.
library_path = "/home/momomizu/Downloads"

yt = YouTube(url=url)
videofile_name = library_path+"/TEMP_video.mp4"
audiofile_name = library_path+"/TEMP_audio.m4a"
title = yt.title

print(library_path)
print(videofile_name)
print(audiofile_name)

def Downloader():
    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('bitrate').desc().first()
    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
    
    #video_stream.download(output_path=library_path)
    #audio_stream.download(output_path=library_path)

    video_stream.download(filename="TEMP_video.mp4", output_path=library_path)
    audio_stream.download(filename="TEMP_audio.m4a", output_path=library_path)

def Converter():

    #video_clip = VideoFileClip(videofile_name)
    #audio_clip = AudioFileClip(audiofile_name)

    video_clip = VideoFileClip(library_path + "/" + "TEMP_video.mp4")
    audio_clip = AudioFileClip(library_path + "/" + "TEMP_audio.m4a")

    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(library_path+"/"+title+".mp4", codec='libx264')

    os.remove(audiofile_name)
    os.remove(videofile_name)


Downloader()
Converter()