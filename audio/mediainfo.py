import os
import json
import subprocess


def info(mov_path):
    subprocess.call('mediainfo --Output=JSON "' + mov_path + '" > mediainfo.json', shell=True)
    with open('mediainfo.json', 'r') as mediainfo_file:
        mediainfo = json.loads(mediainfo_file.read())
        mediainfo_file.close()
    if os.path.exists('mediainfo.json'):
        os.remove('mediainfo.json')

    result = {}
    while True:
        try:
            if (
                    mediainfo['media']['track'][1]['@type'] == 'Video' and
                    (
                            mediainfo['media']['track'][2]['@type'] == 'Audio' and
                            mediainfo['media']['track'][2]['ChannelPositions'] == 'Front: L C R, Side: L R, LFE'
                    ) and
                    (
                            mediainfo['media']['track'][3]['@type'] == 'Audio' and
                            mediainfo['media']['track'][3]['ChannelPositions'] == 'Front: L R'
                    )
            ):  # video + 5.1 + 2.0
                result = {
                    '5_1': {
                        'track': '1'
                    },
                    '2_0': {
                        'track': '2'
                    }
                }
                break
        except KeyError:
            ...
        try:
            if (
                    mediainfo['media']['track'][1]['@type'] == 'Video' and
                    (
                            mediainfo['media']['track'][2]['@type'] == 'Audio' and
                            mediainfo['media']['track'][2]['ChannelPositions'] == 'Front: L R'
                    )
            ):  # video + 2.0
                result = {
                    '2_0': {
                        'track': '1'
                    }
                }
                break
        except KeyError:
            ...
        try:
            if (
                    (
                            mediainfo['media']['track'][1]['@type'] == 'Audio' and
                            mediainfo['media']['track'][1]['ChannelPositions'] == 'Front: L C R, Side: L R, LFE'
                    ) and
                    (
                            mediainfo['media']['track'][2]['@type'] == 'Audio' and
                            mediainfo['media']['track'][2]['ChannelPositions'] == 'Front: L R'
                    )
            ):  # 5.1 + 2.0
                result = {
                    '5_1': {
                        'track': '0'
                    },
                    '2_0': {
                        'track': '1'
                    }
                }
                break
        except KeyError:
            ...
        try:
            if (
                    mediainfo['media']['track'][1]['@type'] == 'Audio' and
                    mediainfo['media']['track'][1]['ChannelPositions'] == 'Front: L R'
            ):  # 2.0
                result = {
                    '2_0': {
                        'track': '0'
                    }
                }
                break
        except KeyError:
            ...
        break

    return result
