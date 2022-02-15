import os
import json
import concurrent.futures
import subprocess

import encode_settings
import video.encode

ladder = encode_settings.encode_settings['ladder']


def concat(key, video_media_info=None, segment_list=None):
    codec = ladder[key]['codec']
    video_fps = video_media_info['video_fps']

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = []
        result_list = {}
        for seg_num in segment_list:
            futures.append(executor.submit(
                video.encode.encode,
                key,
                segmant_num=seg_num,
                video_media_info=video_media_info,
                start_time=segment_list[seg_num]['start_time'],
                start_time_padding=segment_list[seg_num]['start_time_padding'],
                duration=segment_list[seg_num]['duration'],
                duration_padding=segment_list[seg_num]['duration_padding'],
                extract_segment=segment_list[seg_num]['extract_segment'],
                keyint=segment_list[seg_num]['keyint'],
            ))
        for out_file in concurrent.futures.as_completed(futures):
            out_file = out_file.result()
            result_list[out_file['segmant_num']] = out_file

    executor.shutdown()

    '''for seg_num in segment_list:
        video.encode.encode(
            key,
            segmant_num=seg_num,
            video_media_info=video_media_info,
            start_time=segment_list[seg_num]['start_time'],
            start_time_padding=segment_list[seg_num]['start_time_padding'],
            duration=segment_list[seg_num]['duration'],
            duration_padding=segment_list[seg_num]['duration_padding'],
            keyint=segment_list[seg_num]['keyint'],
        )'''

    split_list = []
    for seg in segment_list:
        split_list = split_list + result_list[seg]['split_list']

    ''' build mp4box cmd '''
    if codec == 'avc':
        ext = 'h264'
        bsf = 'h264_mp4toannexb'
    elif codec == 'hevc':
        ext = 'hevc'
        bsf = 'hevc_mp4toannexb'
    else:
        raise ValueError

    with open('cat.txt', 'w') as cat_txt:
        for item in split_list:
            cat_txt.write('file \'' + item + '\'\n')
    cat_txt.close()

    cmd_list = [
        'ffmpeg -f concat -safe 0 -i cat.txt -c copy ' + key + '.mp4',
        'ffmpeg -i ' + key + '.mp4 -bsf:v ' + bsf + ' -c:v copy ' + key + '.' + ext,
    ]
    if not os.path.exists(key + '.' + ext):
        for cmd in cmd_list:
            print(cmd)
            subprocess.call(cmd, shell=True)

    if os.path.exists(key + '.mp4'):
        os.remove(key + '.mp4')
    for item in split_list:
        if os.path.exists(item):
            os.remove(item)
