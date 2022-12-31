import subprocess
import os

import encode_list
import video.get_level
import util


def encode(quality, video_media_info=None):
    ladder = encode_list.read_encode_list()['ladder']

    video_path = video_media_info['video_path']

    video_crop_top = video_media_info['video_crop_top']
    video_crop_left = video_media_info['video_crop_left']

    video_cropped_width = video_media_info['video_cropped_width']
    video_cropped_height = video_media_info['video_cropped_height']

    hls_compatible = video_media_info['hls_compatible']
    hls_compatible_keyint_second = video_media_info['hls_compatible_keyint_second']
    hls_compatible_dynamic_keyint = video_media_info['hls_compatible_dynamic_keyint']

    two_pass_encoding = video_media_info['two_pass_encoding']

    video_fps = video_media_info['video_fps']
    video_fps_float = int(video_fps.split('/')[0]) / int(video_fps.split('/')[1])
    if hls_compatible is True:
        keyint = str(util.math_round(video_fps_float * hls_compatible_keyint_second))
    else:
        keyint = '250'

    codec = ladder[quality]['codec']
    ext = ladder[quality]['ext']
    dr = ladder[quality]['dr']
    codded_width = ladder[quality]['codded_width']
    codded_height = ladder[quality]['codded_width']
    maxrate = ladder[quality]['maxrate']
    max_avg_rate = ladder[quality]['max_avg_rate']
    bufsize = ladder[quality]['bufsize']
    enc_speed = ladder[quality]['encode_speed']
    enc_profile = ladder[quality]['encode_profile']
    encode_extra_settings = ladder[quality]['encode_extra_settings']
    encode_extra_settings = encode_extra_settings.format(fps=str(int(video_fps_float)))
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
        final_height = util.math_round(int(codded_width) / (video_cropped_width / video_cropped_height) / 2) * 2
    else:
        final_width = util.math_round(int(codded_height) * (video_cropped_width / video_cropped_height) / 2) * 2
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
    out_tmp = quality + '.tmp.' + ext
    out_raw = quality + '.' + ext
    out_mp4 = quality + '.mp4'
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
                    zscale + ':matrix=709:transfer=smpte2084:primaries=smpte432,format=gbrpf32le,' +
                    'zscale=matrixin=709:transferin=smpte2084:primariesin=smpte432' +
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
                ' --keyint ' + keyint + ' --min-keyint 1 --scenecut 0'
        )
        keyint_scenecut_hevc = (
                ' --no-open-gop --keyint ' + keyint + ' --min-keyint 1 --scenecut 0'
        )
    else:
        keyint_scenecut_avc = ''
        keyint_scenecut_hevc = ''

    '''encode'''
    if os.path.exists(out_raw):
        return out_raw

    pass_num_avc = ''
    pass_num_hevc = ''
    if two_pass_encoding is True:
        pass_num_avc = ' --pass 1 --slow-firstpass'
        pass_num_hevc = ' --pass 1 --slow-firstpass'

    qp = ''
    if hls_compatible_dynamic_keyint is True:
        qp = ' --qpfile qp.txt'

    cmd_avc = (
        cmd_base +
        'x264 --threads 6 --log-level warning --demuxer y4m' +
        '{pass_num}{bitrate} --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
        ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level +
        keyint_scenecut_avc + ' ' + encode_extra_settings + hdr_settings +
        qp + ' --stats ' + out_state + ' -o "' + out_tmp + '" -'
    )
    cmd_hevc = (
        cmd_base +
        'x265 --frame-threads 1 --log-level warning --y4m' +
        '{pass_num}{bitrate} --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
        ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level +
        keyint_scenecut_hevc + ' ' + encode_extra_settings + hdr_settings +
        qp + ' --stats ' + out_state + ' --analysis-reuse-file ' + out_analysis +
        ' --dither --no-info --repeat-headers --aud --hrd -o "' + out_tmp + '" -'
    )

    if codec == 'avc':
        cmd = [cmd_avc.format(pass_num=pass_num_avc, bitrate=' --crf ' + crf)]
    elif codec == 'hevc':
        cmd = [cmd_hevc.format(pass_num=pass_num_hevc, bitrate=' --crf ' + crf)]
    else:
        raise RuntimeError

    if two_pass_encoding is True:
        cmd.append('mp4box -add "' + out_tmp + '" -new "' + out_mp4 + '"')

    for item in cmd:
        print(item)
        subprocess.call(item, shell=True)

    '''pass 2 rate control'''
    if two_pass_encoding is True:
        pass1_bitrate = int(subprocess.check_output(
            'ffprobe -v error -select_streams "v:0" -show_entries "stream=bit_rate"' +
            ' -of "default=noprint_wrappers=1:nokey=1" "' + out_mp4 + '"',
            shell=True))
        bitrate = util.math_round(pass1_bitrate / 1000)
        bitrate = str(int(min(float(bitrate), float(max_avg_rate))))

        if codec == 'avc':
            cmd = [
                cmd_avc.format(pass_num=' --pass 2 --slow-firstpass', bitrate=' --bitrate ' + bitrate)
            ]
        elif codec == 'hevc':
            cmd = [
                cmd_hevc.format(pass_num=' --pass 2 --slow-firstpass', bitrate=' --bitrate ' + bitrate)
            ]
        else:
            raise RuntimeError

        for item in cmd:
            print(item)
            subprocess.call(item, shell=True)
    else:
        print('max_avg_rate will be ignored if two_pass_encoding is not True.')

    os.rename(out_tmp, out_raw)

    if os.path.exists(out_mp4):
        os.remove(out_mp4)
    if os.path.exists(out_state):
        os.remove(out_state)
    if os.path.exists(out_state + '.mbtree'):
        os.remove(out_state + '.mbtree')
    if os.path.exists(out_state + '.cutree'):
        os.remove(out_state + '.cutree')
    if os.path.exists(out_analysis):
        os.remove(out_analysis)

    return out_raw
