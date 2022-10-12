import subprocess
import os

import encode_list
import video.get_level


def encode(quality, video_media_info=None):
    ladder = encode_list.read_encode_list()['ladder']

    video_path = video_media_info['video_path']

    video_crop_top = video_media_info['video_crop_top']
    video_crop_left = video_media_info['video_crop_left']

    video_cropped_width = video_media_info['video_cropped_width']
    video_cropped_height = video_media_info['video_cropped_height']

    hls_compatible = video_media_info['hls_compatible']
    hls_compatible_keyint_second = video_media_info['hls_compatible_keyint_second']

    video_fps = video_media_info['video_fps']
    video_fps_float = int(video_fps.split('/')[0]) / int(video_fps.split('/')[1])
    if hls_compatible is True:
        keyint = str(round(video_fps_float * hls_compatible_keyint_second))
    else:
        keyint = '250'

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
    out_raw = quality + '.' + ext
    out_state = quality + '.log'
    out_analysis = quality + '.dat'

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

    cmd_base = (
            'ffmpeg -loglevel warning' +
            ' -i "' + video_path + '"' +
            ' -vf "crop=' + crop_settings + zscale + '"' +
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

    '''keyint & scenecut'''
    if hls_compatible is True:
        keyint_scenecut_avc = (
                ' --keyint ' + keyint + ' --min-keyint ' + keyint + ' --scenecut 0'
        )
        keyint_scenecut_hevc = (
                ' --no-open-gop --keyint ' + keyint + ' --min-keyint ' + keyint + ' --scenecut 0'
        )
    else:
        keyint_scenecut_avc = ''
        keyint_scenecut_hevc = ''

    '''encode'''
    if codec == 'avc':
        cmd = [
            cmd_base +
            'x264 --threads 6 --log-level warning --demuxer y4m' +
            ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level +
            keyint_scenecut_avc + ' ' + encode_extra_settings + hdr_settings +
            ' --stitchable -o "' + out_raw + '" -',
        ]
    elif codec == 'hevc':
        cmd = [
            cmd_base +
            'x265 --frame-threads 1 --log-level warning --y4m' +
            ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level +
            keyint_scenecut_hevc + ' ' + encode_extra_settings + hdr_settings +
            ' --no-info --repeat-headers --hrd-concat -o "' + out_raw + '" -',
        ]
    else:
        raise RuntimeError
    out_file = out_raw
    '''skip if completed'''
    if not os.path.exists(out_raw):
        for item in cmd:
            print(item)
            subprocess.call(item, shell=True)

    if os.path.exists(out_state):
        os.remove(out_state)
    if os.path.exists(out_state + '.mbtree'):
        os.remove(out_state + '.mbtree')
    if os.path.exists(out_state + '.cutree'):
        os.remove(out_state + '.cutree')
    if os.path.exists(out_analysis):
        os.remove(out_analysis)

    return out_file
