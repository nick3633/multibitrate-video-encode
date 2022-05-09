import subprocess
import os

import encode_settings
import video.get_level

ladder = encode_settings.encode_settings['ladder']


def encode(
        quality,
        segmant_num='0',
        video_media_info=None,
        start_time=0,
        start_time_padding=0,
        duration=0,
        duration_padding=0,
        keyint='50',
):
    video_path = video_media_info['video_path']

    video_crop_top = video_media_info['video_crop_top']
    video_crop_left = video_media_info['video_crop_left']

    video_cropped_width = video_media_info['video_cropped_width']
    video_cropped_height = video_media_info['video_cropped_height']

    video_fps = video_media_info['video_fps']
    video_fps_float = int(video_fps.split('/')[0]) / int(video_fps.split('/')[1])

    codec = ladder[quality]['codec']
    ext = ladder[quality]['ext']
    dr = ladder[quality]['dr']
    codded_width = ladder[quality]['codded_width']
    codded_height = ladder[quality]['codded_width']
    maxrate = ladder[quality]['maxrate']
    bufsize = ladder[quality]['bufsize']
    enc_speed = ladder[quality]['encode_speed']
    enc_profile = ladder[quality]['encode_profile']
    encode_extra_settings = ladder[quality]['encode_extra_settings']
    crf = ladder[quality]['crf']

    '''pixel format'''
    if dr == 'hdr':
        pix_fmt = 'yuv420p12'
    else:
        pix_fmt = 'yuv420p10'

    '''video crop'''
    crop_settings = (
            str(video_cropped_width) + ':' +
            str(video_cropped_height) + ':' +
            str(video_crop_left) + ':' +
            str(video_crop_top)
    )

    '''video res'''
    if video_cropped_width / video_cropped_height >= 16 / 9:
        final_width = codded_width
        final_height = round(int(codded_width) / (video_cropped_width / video_cropped_height) / 2) * 2
    else:
        final_width = round(int(codded_height) * (video_cropped_width / video_cropped_height) / 2) * 2
        final_height = codded_height
    res_settings = 'width=' + str(final_width) + ':height=' + str(final_height)

    '''level'''
    enc_level = video.get_level.get_level(
        codec,
        int(final_width),
        int(final_height),
        int(maxrate),
        int(bufsize),
        enc_profile,
        video_fps_float
    )

    '''output file name'''
    if not os.path.exists(segmant_num + '/'):
        os.mkdir(segmant_num + '/')
    out_raw = segmant_num + '/' + quality + '.' + ext
    out_raw_tmp = segmant_num + '/tmp.' + ext
    out_mp4 = segmant_num + '/' + quality + '.mp4'
    out_trim_mp4 = segmant_num + '/' + quality + '.trim.mp4'
    out_trim_raw = segmant_num + '/' + quality + '.trim.' + ext
    out_state = segmant_num + '/' + quality + '.log'

    '''trim start:end'''
    mp4box_split_start = str(round((start_time - start_time_padding) / video_fps_float, 9))
    mp4box_split_end = str(round((start_time - start_time_padding + duration) / video_fps_float, 9))

    '''build cmd base'''
    zscale = ',zscale=' + res_settings + ':filter=bicubic'
    if dr == 'hdr':
        if (
                video_media_info['video_colour_primaries'] == 'BT.2020' and
                video_media_info['video_transfer_characteristics'] == 'PQ' and
                video_media_info['video_matrix_coefficients'] == 'BT.2020 non-constant'
        ):
            ...
        elif (
                video_media_info['video_colour_primaries'] == 'Display P3' and
                video_media_info['video_transfer_characteristics'] == 'PQ' and
                video_media_info['video_matrix_coefficients'] == 'BT.709'
        ):
            zscale = (
                    zscale + ':matrixin=709:transferin=smpte2084:primariesin=smpte432' +
                    ':matrix=2020_ncl:transfer=smpte2084:primaries=2020'
            )

    tpad = ''
    if start_time_padding < 0:
        tpad = tpad + ',tpad=start_duration=' + str(round((0 - start_time_padding) / video_fps_float, 9))
        duration_padding = duration_padding + start_time_padding
        start_time_padding = 0
    if (start_time_padding + duration_padding) > video_media_info['video_frame_count']:
        tpad = tpad + ',tpad=stop_duration=' + str(round((start_time_padding + duration_padding -
                                                          video_media_info['video_frame_count']) / video_fps_float, 9))
        duration_padding = video_media_info['video_frame_count'] - start_time_padding
        start_time_padding = start_time_padding

    cmd_base = (
            'ffmpeg -loglevel warning' +
            ' -ss ' + str(round(start_time_padding / video_fps_float, 9)) +
            ' -t ' + str(round(duration_padding / video_fps_float, 9)) +
            ' -i "' + video_path + '"' +
            ' -vf "crop=' + crop_settings + zscale + tpad + '"' +
            ' -pix_fmt ' + pix_fmt + ' -strict -1 -f yuv4mpegpipe -y - | '
    )

    ''' dynamic range and color space settings '''
    hdr_settings = ''
    if codec == 'avc':
        hdr_settings = ' --range tv --colorprim bt709 --transfer bt709 --colormatrix bt709'
    elif codec == 'hevc':
        hdr_settings = ' --range limited --colorprim bt709 --transfer bt709 --colormatrix bt709'
    if dr == 'hdr':
        hdr_settings = (
                ' --range limited --colorprim bt2020 --transfer smpte2084 --colormatrix bt2020nc' +
                ' --hdr10 --hdr10-opt' +
                ' --master-display "' + video_media_info['video_master_display'] + '"' +
                ' --max-cll "' + video_media_info['video_cll'] + '"'
        )

    '''encode'''
    if not os.path.exists(out_raw):
        if codec == 'avc':
            cmd = [
                cmd_base +
                'x264 --threads 1 --log-level warning --demuxer y4m' +
                ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
                ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level +
                ' --keyint ' + keyint + ' --min-keyint ' + keyint + ' --scenecut 0' +
                ' --rc-lookahead ' + str(round(video_fps_float * 2)) + ' ' + encode_extra_settings + hdr_settings +
                ' --stitchable -o "' + out_raw_tmp + '" -',
            ]
        elif codec == 'hevc':
            cmd = [
                cmd_base +
                'x265 --frame-threads 1 --no-wpp --log-level warning --y4m' +
                ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
                ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level + ' --high-tier' +
                ' --no-open-gop --keyint ' + keyint + ' --min-keyint ' + keyint + ' --scenecut 0 --scenecut-bias 0' +
                ' --rc-lookahead ' + str(round(video_fps_float * 2)) + ' ' + encode_extra_settings + hdr_settings +
                ' --no-info --repeat-headers --hrd-concat -o "' + out_raw_tmp + '" -',
            ]
        else:
            raise RuntimeError
        for item in cmd:
            print(item)
            subprocess.call(item, shell=True)

        os.rename(out_raw_tmp, out_raw)

        if os.path.exists(out_state):
            os.remove(out_state)
        if os.path.exists(out_state + '.mbtree'):
            os.remove(out_state + '.mbtree')
        if os.path.exists(out_state + '.cutree'):
            os.remove(out_state + '.cutree')
        if os.path.exists(out_state + '.dat'):
            os.remove(out_state + '.dat')

    '''trim'''
    cmd = [
        'MP4Box -add ' + out_raw + ' -new ' + out_mp4,
        'MP4Box -splitz ' + mp4box_split_start + ':' + mp4box_split_end + ' ' + out_mp4 + ' -out ' + out_trim_mp4,
        'MP4Box -raw 1:output=' + out_trim_raw + ' ' + out_trim_mp4,
    ]
    for item in cmd:
        print(item)
        subprocess.call(item, shell=True)

    split_list = [out_trim_raw]
    if os.path.exists(out_mp4):
        os.remove(out_mp4)
    if os.path.exists(out_trim_mp4):
        os.remove(out_trim_mp4)

    return {
        'segmant_num': segmant_num,
        'split_list': split_list,
    }
