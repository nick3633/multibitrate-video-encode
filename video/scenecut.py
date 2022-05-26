import os
import subprocess
import json


def scenecut_list(video_info):
    if os.path.exists('segment_list.json'):
        with open('segment_list.json', 'r') as segment_list_file:
            return json.loads(segment_list_file.read())

    video_path = video_info['video_path']

    video_crop_top = video_info['video_crop_top']
    video_crop_left = video_info['video_crop_left']
    video_cropped_width = video_info['video_cropped_width']
    video_cropped_height = video_info['video_cropped_height']

    video_frame_count = video_info['video_frame_count']
    video_fps = video_info['video_fps']
    video_fps_float = int(video_fps.split('/')[0]) / int(video_fps.split('/')[1])

    scenecut_start_frame = [0]
    cut_type = {}
    segmant_list = {}

    '''video crop'''
    crop_settings = (
            str(video_cropped_width) + ':' +
            str(video_cropped_height) + ':' +
            str(video_crop_left) + ':' +
            str(video_crop_top)
    )

    '''video res'''
    if video_cropped_width / video_cropped_height >= 16 / 9:
        res_settings = 'width=1280:height=-2'
    else:
        res_settings = 'width=-2:height=720'

    '''build cmd base'''
    zscale = ',zscale=' + res_settings + ':filter=bicubic'

    cmd = [
            'ffmpeg -loglevel warning -i "' + video_path + '"' +
            ' -sws_flags bicubic+accurate_rnd+full_chroma_int+full_chroma_inp+bitexact -sws_dither none' +
            ' -vf "crop=' + crop_settings + zscale + '"' +
            ' -pix_fmt yuv420p10 -strict -1 -f yuv4mpegpipe -y - | ' +
            'x265 --y4m' +
            ' --crf 23 --preset medium --profile main10' +
            ' --no-open-gop --keyint ' + str(video_frame_count + 1) + ' --min-keyint ' + str(round(video_fps_float)) +
            ' --rc-lookahead ' + str(round(video_fps_float * 2)) +
            ' --no-info --repeat-headers --hrd-concat -o "scenecut.265" -',
            'MP4Box -add "scenecut.265" -new "scenecut.mp4"'
    ]

    if not os.path.exists('scenecut.mp4'):
        for i in cmd:
            print(cmd)
            subprocess.call(i, shell=True)
    if os.path.exists('scenecut.265'):
        os.remove('scenecut.265')

    cmd = 'ffprobe -v error -show_entries frame=pict_type -of json scenecut.mp4 > frame_type.json'
    if not os.path.exists('frame_type.json'):
        print(cmd)
        subprocess.call(cmd, shell=True)

    scenecut_json = json.loads(open('frame_type.json', 'r').read())
    i = 0
    for frame in scenecut_json['frames']:
        if frame['pict_type'] == 'I':
            scenecut_start_frame.append(i)
            cut_type[i] = 'scenecut'
        i = i + 1

    scenecut_start_frame.append(video_frame_count)
    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))

    restart = True
    while restart is True:
        i = 0
        for item in scenecut_start_frame:
            try:
                if scenecut_start_frame[i + 1] - item < round(video_fps_float * 1):
                    del scenecut_start_frame[i + 1]
                    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))
                    break
                '''if scenecut_start_frame[i + 1] - item > round(video_fps_float * 60 * 3):
                    new_scenecut = round((item + scenecut_start_frame[i + 1]) / 2)
                    new_scenecut = round(video_fps_float) * round(new_scenecut / round(video_fps_float))
                    scenecut_start_frame.append(new_scenecut)
                    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))
                    break'''
            except IndexError:
                restart = False
            i = i + 1
    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))

    scenecut_start_frame = scenecut_start_frame[:-1]
    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))

    n = 0
    for point in scenecut_start_frame:
        start_time = point
        try:
            duration = (scenecut_start_frame[n + 1] - point)
        except IndexError:
            duration = (video_frame_count - point)

        keyint = str(round(video_fps_float * 6))
        start_time_padding = start_time - round(video_fps_float * 2)
        duration_padding = duration + round(video_fps_float * 2) + round(video_fps_float * 2)

        segmant_list[str(n)] = {
            'start_time': int(start_time),
            'start_time_padding': int(start_time_padding),
            'duration': int(duration),
            'duration_padding': int(duration_padding),
            'keyint': keyint,
        }
        n = n + 1

        with open('segment_list.json', 'w') as segment_list_file:
            segment_list_file.write(json.dumps(segmant_list, indent=2))

    return segmant_list
