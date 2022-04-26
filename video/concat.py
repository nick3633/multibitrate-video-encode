import os
import concurrent.futures
import subprocess
import multiprocessing

import encode_settings
import video.encode

ladder = encode_settings.encode_settings['ladder']


def concat(key, video_media_info=None, segment_list=None):
    ext = ladder[key]['ext']
    worker_num = max(int(multiprocessing.cpu_count() * 0.5), 1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_num) as executor:
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
    i = 0
    for item in split_list:
        if i < 1:
            subprocess.call('mp4box -add "' + item + '" -new tmp2.mp4', shell=True)
        else:
            subprocess.call('mp4box -add tmp.mp4 -cat "' + item + '" -new tmp2.mp4', shell=True)
            os.remove('tmp.mp4')
        os.rename('tmp2.mp4', 'tmp.mp4')
        i = i + 1

    cmd_list = [
        'mp4box -raw 1:output=' + key + '.' + ext + ' "tmp.mp4"'
    ]
    if not os.path.exists(key + '.' + ext):
        for cmd in cmd_list:
            print(cmd)
            subprocess.call(cmd, shell=True)

    for item in split_list:
        if os.path.exists(item):
            os.remove(item)
    if os.path.exists('tmp.mp4'):
        os.remove('tmp.mp4')
