import subprocess
import os

import encode_settings

ladder = encode_settings.encode_settings['ladder']


def encode(quality, video_media_info=None):
    video_path = video_media_info['video_path']

    video_crop_top = video_media_info['video_crop_top']
    video_crop_left = video_media_info['video_crop_left']

    video_cropped_width = video_media_info['video_cropped_width']
    video_cropped_height = video_media_info['video_cropped_height']

    codec = ladder[quality]['codec']
    ext = ladder[quality]['ext']
    dr = ladder[quality]['dr']
    codded_width = ladder[quality]['codded_width']
    codded_height = ladder[quality]['codded_width']
    maxrate = ladder[quality]['maxrate']
    bufsize = ladder[quality]['bufsize']
    encode_speed = ladder[quality]['encode_speed']
    encode_profile = ladder[quality]['encode_profile']
    encode_level = ladder[quality]['encode_level']
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
        res_settings = 'width=' + codded_width + ':height=-2'
    else:
        res_settings = 'width=-2:height=' + codded_height

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

    '''output file name'''
    out_raw = quality + '.' + ext
    out_state = quality + '.log'
    out_analysis = quality + '.dat'

    '''skip if completed'''
    if os.path.exists(out_raw):
        return None

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

    '''pass 1'''
    if codec == 'avc':
        cmd = [
            cmd_base +
            'x264 --threads 1 --log-level warning --demuxer y4m' +
            ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset ' + encode_speed + ' --profile ' + encode_profile + ' --level ' + encode_level +
            ' --open-gop --keyint 50 --rc-lookahead 50 ' + encode_extra_settings + hdr_settings +
            ' --stats ' + out_state + ' --output "' + out_raw + '" -',
        ]
    elif codec == 'hevc':
        cmd = [
            cmd_base +
            'x265 --frame-threads 1 --log-level warning --y4m' +
            ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset ' + encode_speed + ' --profile ' + encode_profile + ' --level ' + encode_level +
            ' --high-tier --repeat-headers --aud --hrd' +
            ' --open-gop --keyint 50 --rc-lookahead 50 ' + encode_extra_settings + hdr_settings +
            ' --no-info --stats ' + out_state + ' --output "' + out_raw + '" -',
        ]
    else:
        raise RuntimeError
    out_file = out_raw
    for item in cmd:
        print(item)
        subprocess.call(item, shell=True)

    if os.path.exists(out_state):
        os.remove(out_state)
    if os.path.exists(out_state + '.mbtree'):
        os.remove(out_state + '.mbtree')
    if os.path.exists(out_state + '.cutree'):
        os.remove(out_state + '.cutree')
    if os.path.exists(out_state + '.dat'):
        os.remove(out_state + '.dat')

    return out_file
