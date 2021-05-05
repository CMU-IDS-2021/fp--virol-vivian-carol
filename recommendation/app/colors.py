from django.contrib.staticfiles.storage import staticfiles_storage

from pytube import YouTube
import cv2
import os 
import shutil
from PIL import Image, ImageStat, ImageDraw
import numpy as np

#Get average color of frames
def get_average_color(image_name, color_list, frame_folder):
  image = Image.open(frame_folder+"/"+image_name)
  average = ImageStat.Stat(image).mean
  color_list.append(average)
  
def get_color_list(download_folder, download_name, frame_folder):
  #Get frames from video (once every second)
  vidcap = cv2.VideoCapture(download_folder+"/"+download_name+".mp4")
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  success,image = vidcap.read()
  count = 0
  color_list = []
  while success:
    if count % round(fps) == 0:
      frame_name = "frame%d.jpg" % count
      cv2.imwrite(frame_folder+"/"+frame_name, image)     # save frame as JPEG file
      get_average_color(frame_name, color_list, frame_folder)
    success,image = vidcap.read()
    count += 1
  return color_list

def image_scale(index, scale):
  return int(index * scale)

def average_colors(title, video_url):
  download_folder = staticfiles_storage.path("downloads/")
  frame_folder = os.path.join(download_folder,"frames")
  download_name = "test"

  #Make sure folders exist
  os.makedirs(download_folder, exist_ok=True)
  os.makedirs(frame_folder, exist_ok=True)

  #Download video
  if not os.path.isfile(f'app/static/app/images/{title}.png') or title == 'originalmovie':
    try:
      video = YouTube(video_url)
      stream = video.streams.filter(mime_type="video/mp4",res="360p")[0]
      stream.download(download_folder, download_name)

      color_list = get_color_list(download_folder, download_name, frame_folder)
      output_image = Image.new('RGB', (len(color_list), len(color_list)), color = 'white')
      d = ImageDraw.Draw(output_image)

      for index, value in enumerate(color_list):
        d.line((index,len(color_list), index, 0), fill=(int(value[0]),int(value[1]),int(value[2])))
      
      output_image = output_image.resize((1920,1080),resample=Image.BILINEAR)
      output_image.format = "PNG"
      output_image.save(f'app/static/app/images/{title}.png', format="PNG")

      return f'{title}.png'
    except Exception as e:
      print(e)
      return ''
  else:
    return f'{title}.png'
  