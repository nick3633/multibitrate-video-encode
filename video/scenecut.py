import os
import subprocess
import json

import util


def scenecut_list(video_info, output_segment_list=False, output_qpfile=True, chunked_encoding=True):
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

    hls_compatible = video_info['hls_compatible']
    hls_compatible_dynamic_keyint = video_info['hls_compatible_dynamic_keyint']
    hls_compatible_keyint = video_info['hls_compatible_keyint']


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
            'ffmpeg -loglevel warning -i "' + video_path + '" -vf "crop=' + crop_settings + zscale + '"' +
            ' -pix_fmt yuv420p10 -strict -1 -f yuv4mpegpipe -y - | ' +
            'x264 --demuxer y4m --crf 23 --keyint ' + str(video_frame_count + 1) + ' -o "scenecut.h264" -',
            'MP4Box -add "scenecut.h264" -new "scenecut.mp4"'
    ]

    if not os.path.exists('scenecut.mp4'):
        for i in cmd:
            print(cmd)
            subprocess.call(i, shell=True)
    if os.path.exists('scenecut.h264'):
        os.remove('scenecut.h264')

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
                if scenecut_start_frame[i + 1] - item < int(video_fps_float * 1):
                    del scenecut_start_frame[i + 1]
                    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))
                    break
                '''if scenecut_start_frame[i + 1] - item > util.math_round(video_fps_float * 60 * 3):
                    new_scenecut = util.math_round((item + scenecut_start_frame[i + 1]) / 2)
                    new_scenecut = util.math_round(video_fps_float) * util.math_round(new_scenecut / util.math_round(video_fps_float))
                    scenecut_start_frame.append(new_scenecut)
                    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))
                    break'''
            except IndexError:
                restart = False
            i = i + 1
    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))

    scenecut_start_frame = scenecut_start_frame[:-1]
    scenecut_start_frame = sorted(list(dict.fromkeys(scenecut_start_frame)))

    if hls_compatible is True:
        if hls_compatible_keyint[1] == 's':
            keyint = str(util.math_round(video_fps_float * hls_compatible_keyint[0]))
        elif hls_compatible_keyint[1] == 'f':
            keyint = str(util.math_round(hls_compatible_keyint[0]))
        else:
            keyint = str(util.math_round(video_fps_float * hls_compatible_keyint[0]))

    else:
        keyint = None
    n = 0
    qpfile_string = ''
    for point in scenecut_start_frame:
        start_time = point
        try:
            duration = (scenecut_start_frame[n + 1] - point)
        except IndexError:
            duration = (video_frame_count - point)

        start_time_padding = start_time - 60
        duration_padding = duration + 60 + 60

        segmant_list[str(n)] = {
            'start_time': int(start_time),
            'start_time_padding': int(start_time_padding),
            'duration': int(duration),
            'duration_padding': int(duration_padding),
            'hls_compatible': hls_compatible,
            'keyint': keyint,
        }
        qpfile_string += str(int(start_time + 60)) + ' I\n'
        n = n + 1
    qpfile_string += str(int(video_frame_count + 60)) + ' I\n'

    if chunked_encoding is False:
        segmant_list = {
            "0": {
                'start_time': 0,
                'start_time_padding': int(0 - 60),
                'duration': int(video_frame_count),
                'duration_padding': int(video_frame_count + 60 + 60),
                'hls_compatible': hls_compatible,
                'keyint': keyint,
            }
        }
        if hls_compatible_dynamic_keyint is False:
            qpfile_string = str(int(60)) + ' I\n'
            qpfile_string += str(int(video_frame_count + 60)) + ' I\n'
        if output_qpfile is True:
            if not os.path.exists('0/'):
                os.mkdir('0/')
            with open('0/qp.txt', 'w') as qpfile:
                qpfile.write(qpfile_string)

    if output_segment_list is True:
        with open('segment_list.json', 'w') as segment_list_file:
            segment_list_file.write(json.dumps(segmant_list, indent=2))

    return segmant_list
