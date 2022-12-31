import os
import concurrent.futures
import subprocess
import multiprocessing
import encode_list
import video.encode


def concat(quality, video_media_info=None, segment_list=None):
    ladder = encode_list.read_encode_list()['ladder']

    ext = ladder[quality]['ext']
    worker_num = max(int(multiprocessing.cpu_count() / 2), 1)

    final = quality + '.' + ext
    tmp_mp4 = quality + '.tmp.mp4'
    tmp_raw = quality + '.tmp.' + ext

    if os.path.exists(final):
        return None

    segment_list_key_sorted = {}
    for key in segment_list:
        segment_list_key_sorted[key] = segment_list[key]['duration_padding']
    segment_list_key_sorted = dict(sorted(segment_list_key_sorted.items(), key=lambda item: item[1], reverse=True))

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_num) as executor:
        futures = []
        result_list = {}
        for seg_num in segment_list_key_sorted:
            futures.append(executor.submit(
                video.encode.encode,
                quality,
                segmant_num=seg_num,
                video_media_info=video_media_info,
                start_time=segment_list[seg_num]['start_time'],
                start_time_padding=segment_list[seg_num]['start_time_padding'],
                duration=segment_list[seg_num]['duration'],
                duration_padding=segment_list[seg_num]['duration_padding'],
                keyint=segment_list[seg_num]['keyint'],
            ))
        for out_file in concurrent.futures.as_completed(futures):
            out_file = out_file.result()
            result_list[out_file['segmant_num']] = out_file

    executor.shutdown()

    split_list = []
    for seg in segment_list:
        split_list = split_list + result_list[seg]['split_list']

    ''' build mp4box cmd '''
    with open(tmp_raw, 'ab') as concat_file:
        for item in split_list:
            concat_file.write(open(item, 'rb').read())

    cmd_list = [
        'MP4Box -add "' + tmp_raw + '" -new "' + tmp_mp4 + '"',
        'MP4Box -raw 1:output=' + final + ' "' + tmp_mp4 + '"'
    ]
    for cmd in cmd_list:
        print(cmd)
        subprocess.call(cmd, shell=True)

    for item in split_list:
        if os.path.exists(item):
            os.remove(item)
    if os.path.exists(tmp_mp4):
        os.remove(tmp_mp4)
    if os.path.exists(tmp_raw):
        os.remove(tmp_raw)
