import os
import json
import subprocess


def info(video_path, video_metadata, dr):
    subprocess.call('mediainfo --Output=JSON "' + video_path + '" > mediainfo.json', shell=True)
    with open('mediainfo.json', 'r') as mediainfo_file:
        mediainfo = json.loads(mediainfo_file.read())
        mediainfo_file.close()
    if os.path.exists('mediainfo.json'):
        os.remove('mediainfo.json')

    video_width = int(mediainfo['media']['track'][1]['Width'])
    video_height = int(mediainfo['media']['track'][1]['Height'])
    video_cropped_width = video_width - video_metadata['crop']['left'] - video_metadata['crop']['right']
    video_cropped_height = video_height - video_metadata['crop']['top'] - video_metadata['crop']['bottom']

    if dr == 'hdr':
        video_colour_primaries = mediainfo['media']['track'][1]['colour_primaries']
        video_transfer_characteristics = mediainfo['media']['track'][1]['transfer_characteristics']
        video_matrix_coefficients = mediainfo['media']['track'][1]['matrix_coefficients']
    else:
        video_colour_primaries = mediainfo['media']['track'][1]['colour_primaries']
        video_transfer_characteristics = ''
        video_matrix_coefficients = mediainfo['media']['track'][1]['matrix_coefficients']

    return {
        'video_width': video_width,
        'video_height': video_height,
        'video_cropped_width': video_cropped_width,
        'video_cropped_height': video_cropped_height,
        'video_colour_primaries': video_colour_primaries,
        'video_transfer_characteristics': video_transfer_characteristics,
        'video_matrix_coefficients': video_matrix_coefficients,
    }

