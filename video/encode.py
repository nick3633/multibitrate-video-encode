import subprocess
import os
import pathlib

import encode_list
import video.get_level
import util


def encode(
        quality,
        segmant_num='0',
        video_media_info=None,
        start_time=0,
        start_time_padding=0,
        duration=0,
        duration_padding=0,
        keyint="",
):
    ladder = encode_list.read_encode_list()['ladder']

    video_path = video_media_info['video_path']

    video_crop_top = video_media_info['video_crop_top']
    video_crop_left = video_media_info['video_crop_left']

    video_cropped_width = video_media_info['video_cropped_width']
    video_cropped_height = video_media_info['video_cropped_height']

    hls_compatible = video_media_info['hls_compatible']

    two_pass_encoding = video_media_info['two_pass_encoding']

    video_fps = video_media_info['video_fps']
    video_fps_float = int(video_fps.split('/')[0]) / int(video_fps.split('/')[1])

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
    pathlib.Path(segmant_num).mkdir(parents=True, exist_ok=True)
    out_raw = segmant_num + '/' + quality + '.' + ext
    out_raw_tmp = segmant_num + '/' + quality + '.tmp.' + ext
    out_mp4 = segmant_num + '/' + quality + '.mp4'
    out_trim_mp4 = segmant_num + '/' + quality + '.trim.mp4'
    out_trim_raw = segmant_num + '/' + quality + '.trim.' + ext
    out_state = segmant_num + '/' + quality + '.log'
    out_analysis = segmant_num + '/' + quality + '.dat'
    out_qp = segmant_num + '/qp.txt'

    ''' avc qp '''
    mp4box_split_start = str(util.math_round((start_time - start_time_padding) / video_fps_float, 9))
    mp4box_split_end = str(util.math_round((start_time - start_time_padding + duration) / video_fps_float, 9))
    keyframe_min = start_time - start_time_padding
    keyframe_max = start_time - start_time_padding + duration
    force_keyframe_list = [keyframe_min, keyframe_max]
    qpfile_string = ''
    for force_keyframe in force_keyframe_list:
        frame_type = 'I'
        qpfile_string = qpfile_string + str(force_keyframe) + ' ' + frame_type + '\n'
    if not os.path.exists(out_qp):
        with open(out_qp, 'w') as qpfile:
            qpfile.write(qpfile_string)

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

    tpad = []
    if start_time_padding < 0:
        tpad.append('start_duration=' + str(util.math_round((0 - start_time_padding) / video_fps_float, 9)))
        duration_padding = duration_padding + start_time_padding
        start_time_padding = 0
    if (start_time_padding + duration_padding) > video_media_info['video_frame_count']:
        tpad.append('stop_duration=' + str(util.math_round((start_time_padding + duration_padding - video_media_info['video_frame_count']) / video_fps_float, 9)))
        duration_padding = video_media_info['video_frame_count'] - start_time_padding
        start_time_padding = start_time_padding

    tpad_param = ''
    if tpad:
        tpad_param = ',tpad='
        for item in tpad:
            tpad_param += (item + ':')
        tpad_param = tpad_param[:-1]
    tpad = tpad_param

    cmd_base = (
            'ffmpeg -loglevel warning' +
            ' -ss ' + str(util.math_round(start_time_padding / video_fps_float, 9)) +
            ' -t ' + str(util.math_round(duration_padding / video_fps_float, 9)) +
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
        keyint_scenecut_hevc = ' --no-open-gop'

    '''encode'''
    bitrate_option = ' --crf ' + crf

    cmd_avc = (
            cmd_base +
            'x264 --threads 1 --log-level warning --demuxer y4m' +
            '{pass_num}{bitrate} --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level ' + enc_level +
            keyint_scenecut_avc + ' ' + encode_extra_settings + hdr_settings +
            ' --stitchable --qpfile "' + out_qp + '" --stats ' + out_state + ' -o "' + out_raw_tmp + '" -'
    )
    cmd_hevc = (
            cmd_base +
            'x265 --frame-threads 1 --no-wpp --log-level warning --y4m' +
            '{pass_num}{bitrate} --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset ' + enc_speed + ' --profile ' + enc_profile + ' --level-idc ' + enc_level +
            keyint_scenecut_hevc + ' ' + encode_extra_settings + hdr_settings +
            ' --qpfile "' + out_qp + '" --stats ' + out_state + ' --analysis-reuse-file ' + out_analysis +
            ' --dither --no-info --repeat-headers --aud --hrd --hrd-concat -o "' + out_raw_tmp + '" -'
    )

    if codec == 'avc':
        cmd = [cmd_avc.format(pass_num='', bitrate=bitrate_option)]
    elif codec == 'hevc':
        cmd = [cmd_hevc.format(pass_num='', bitrate=bitrate_option)]
    else:
        raise RuntimeError

    if two_pass_encoding is True:
        cmd.append('mp4box -add "' + out_raw_tmp + '" -new "' + out_mp4 + '"')

    if not os.path.exists(out_raw):
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

            pass1_option = ' --pass 1 --slow-firstpass'
            pass2_option = ' --pass 2 --slow-firstpass'
            bitrate_option = ' --bitrate ' + bitrate

            if codec == 'avc':
                cmd = [
                    cmd_avc.format(pass_num=pass1_option, bitrate=bitrate_option),
                    cmd_avc.format(pass_num=pass2_option, bitrate=bitrate_option)
                ]
            elif codec == 'hevc':
                cmd = [
                    cmd_hevc.format(pass_num=pass1_option, bitrate=bitrate_option),
                    cmd_hevc.format(pass_num=pass2_option, bitrate=bitrate_option)
                ]
            else:
                raise RuntimeError

            for item in cmd:
                print(item)
                subprocess.call(item, shell=True)
        else:
            print('max_avg_rate will be ignored if two_pass_encoding is not True.')

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
