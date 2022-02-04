import os
import json
import subprocess

import encode


# package_dir = sys.argv[1]
def main(package_dir):
    with open(os.path.join(package_dir, 'metadata.json'), 'r') as package_file:
        package = json.loads(package_file.read())
        package_file.close()

    video_path = os.path.join(package_dir, package['video']['path'])
    video_crop_top = int(package['video']['crop_top'])
    video_crop_bottom = int(package['video']['crop_bottom'])
    video_crop_left = int(package['video']['crop_left'])
    video_crop_right = int(package['video']['crop_right'])

    # video MediaInfo
    subprocess.call('mediainfo --Output=JSON "' + video_path + '" > mediainfo.json', shell=True)
    with open('mediainfo.json', 'r') as mediainfo_file:
        mediainfo = json.loads(mediainfo_file.read())
        mediainfo_file.close()
    if os.path.exists('mediainfo.json'):
        os.remove('mediainfo.json')

    video_width = int(mediainfo['media']['track'][1]['Width'])
    video_height = int(mediainfo['media']['track'][1]['Height'])
    video_cropped_width = video_width - video_crop_left - video_crop_right
    video_cropped_height = video_height - video_crop_top - video_crop_bottom

    video_media_info = {
        'video_path': video_path,
        'video_crop_top': video_crop_top,
        'video_crop_bottom': video_crop_bottom,
        'video_crop_left': video_crop_left,
        'video_crop_right': video_crop_right,
        'video_width': video_width,
        'video_height': video_height,
        'video_cropped_width': video_cropped_width,
        'video_cropped_height': video_cropped_height,
    }

    if video_cropped_width >= 3840 or video_cropped_height >= 2160:
        # encode.encode('2160p.hevc', video_media_info=video_media_info)
        ...
    if video_cropped_width >= 1920 or video_cropped_height >= 1080:
        encode.encode('1080p.avc', video_media_info=video_media_info)
        encode.encode('1080p.hevc', video_media_info=video_media_info)
    # encode.encode('480p.avc', video_media_info=video_media_info)
    # encode.encode('480p.hevc', video_media_info=video_media_info)
