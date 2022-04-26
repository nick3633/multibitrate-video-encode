import subprocess
import os

import encode_settings

ladder = encode_settings.encode_settings['ladder']


def encode(
        quality,
        segmant_num='0',
        video_media_info=None,
        start_time=0,
        start_time_padding=0,
        duration=0,
        duration_padding=0,
        extract_segment=None,
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

    '''output file name'''
    if not os.path.exists(segmant_num + '/'):
        os.mkdir(segmant_num + '/')
    out_avc_raw = segmant_num + '/' + quality + '.avc'
    out_hevc_raw = segmant_num + '/' + quality + '.hevc'
    out_mp4 = segmant_num + '/' + quality + '.mp4'
    out_state = segmant_num + '/' + quality + '.log'
    if codec == 'avc':
        out_raw = out_avc_raw
    elif codec == 'hevc':
        out_raw = out_hevc_raw
    else:
        raise RuntimeError

    ''' qp '''
    force_keyframe_list = [
        str(start_time - start_time_padding),
        str(start_time - start_time_padding + duration),
    ]
    qpfile_string = ''
    for force_keyframe in force_keyframe_list:
        qpfile_string = qpfile_string + force_keyframe + ' I' + '\n'
    qpfile_path = segmant_num + '/' + 'qpfile.txt'
    qpfile = open(qpfile_path, 'w')
    qpfile.write(qpfile_string)
    qpfile.close()

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
        tpad = ',tpad=start_duration=' + str((0 - start_time_padding) / video_fps_float)
        duration_padding = duration_padding - (0 - start_time_padding)
        start_time_padding = 0
    if duration_padding > video_media_info['video_frame_count']:
        tpad = ',tpad=stop_duration=' + str((duration_padding - duration) / video_fps_float)
        duration_padding = duration_padding - (duration_padding - (video_media_info['video_frame_count'] - start_time))

    cmd_base = (
            'ffmpeg -loglevel warning' +
            ' -ss ' + str(start_time_padding / video_fps_float) + ' -t ' + str(duration_padding / video_fps_float) +
            ' -i "' + video_path + '"' +
            ' -vf "crop=' + crop_settings + zscale + tpad + '"' +
            ' -pix_fmt ' + pix_fmt + ' -strict -1 -f yuv4mpegpipe -y - | '
    )

    ''' split list '''
    count = 0
    recat_list = ''
    split_list = []
    for i in extract_segment:
        i = str(i).zfill(3)
        if count == 0:
            recat_list = recat_list + ' -add ' + segmant_num + '/' + quality + '_' + i + '.mp4'
        else:
            recat_list = recat_list + ' -cat ' + segmant_num + '/' + quality + '_' + i + '.mp4'
        split_list.append(segmant_num + '/' + quality + '_' + i + '.mp4')
        count = count + 1

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

    if not os.path.exists(out_raw):
        '''pass 1'''
        if codec == 'avc':
            cmd = [
                cmd_base +
                'x264 --threads 1 --pass 1 --log-level warning --demuxer y4m' +
                ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
                ' --preset ' + encode_speed + ' --profile ' + encode_profile + ' --level ' + encode_level +
                ' --keyint ' + keyint + ' --min-keyint 1 --scenecut 0 --stitchable' +
                ' --rc-lookahead ' + str(round(video_fps_float * 2)) + ' ' + encode_extra_settings + hdr_settings +
                ' --stats ' + out_state + ' --qpfile "' + qpfile_path + '" --output "' + out_avc_raw + '" -',
                'mp4box -add "' + out_avc_raw + '" -new "' + out_mp4 + '"'
            ]
        elif codec == 'hevc':
            cmd = [
                cmd_base +
                'x265 --frame-threads 1 --pass 1 --log-level warning --y4m' +
                ' --crf ' + crf + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
                ' --preset ' + encode_speed + ' --profile ' + encode_profile + ' --level ' + encode_level +
                ' --high-tier --repeat-headers --aud --hrd --no-open-gop --keyint ' + keyint + ' --min-keyint 1' +
                ' --scenecut 0 --scenecut-bias 0 --rc-lookahead ' + str(round(video_fps_float * 2)) + ' ' +
                encode_extra_settings + hdr_settings + ' --hrd-concat' +
                ' --no-info --stats ' + out_state + ' --qpfile "' + qpfile_path + '" --output "' + out_hevc_raw + '" -',
                'mp4box -add "' + out_hevc_raw + '" -new "' + out_mp4 + '"'
            ]
        else:
            raise RuntimeError
        for item in cmd:
            print(item)
            subprocess.call(item, shell=True)

        '''pass 2 rate control'''
        cmd = (
                'ffprobe -v error -select_streams "v:0" -show_entries "stream=bit_rate" ' +
                '-of "default=noprint_wrappers=1:nokey=1" "' + out_mp4 + '"'
        )
        print(cmd)
        pass1_bitrate = int(subprocess.check_output(cmd, shell=True))
        bitrate = str(round(pass1_bitrate / 1000))
        if os.path.exists(out_mp4):
            os.remove(out_mp4)

        '''pass 2'''
        if codec == 'avc':
            cmd = [
                cmd_base +
                'x264 --threads 1 --pass 2 --log-level warning --demuxer y4m' +
                ' --bitrate ' + bitrate + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
                ' --preset ' + encode_speed + ' --profile ' + encode_profile + ' --level ' + encode_level +
                ' --keyint ' + keyint + ' --min-keyint 1 --scenecut 0 --stitchable' +
                ' --rc-lookahead ' + str(round(video_fps_float * 2)) + ' ' + encode_extra_settings + hdr_settings +
                ' --stats ' + out_state + ' --qpfile "' + qpfile_path + '" --output "' + out_avc_raw + '" -',
            ]
        elif codec == 'hevc':
            cmd = [
                cmd_base +
                'x265 --frame-threads 1 --pass 2 --log-level warning --y4m' +
                ' --bitrate ' + bitrate + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
                ' --preset ' + encode_speed + ' --profile ' + encode_profile + ' --level ' + encode_level +
                ' --high-tier --repeat-headers --aud --hrd --no-open-gop --keyint ' + keyint + ' --min-keyint 1' +
                ' --scenecut 0 --scenecut-bias 0 --rc-lookahead ' + str(round(video_fps_float * 2)) + ' ' +
                encode_extra_settings + hdr_settings + ' --hrd-concat' +
                ' --no-info --stats ' + out_state + ' --qpfile "' + qpfile_path + '" --output "' + out_hevc_raw + '" -',
            ]
        else:
            raise RuntimeError
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

    cmd = [
        'mp4box -add ' + out_raw + ' -new ' + out_mp4,
        'mp4box -splitr 0 ' + out_mp4,
    ]
    for item in cmd:
        print(item)
        subprocess.call(item, shell=True)

    extract_segment_min = segmant_num + '/' + quality + '_' + str(extract_segment[0] - 1).zfill(3) + '.mp4'
    extract_segment_max = segmant_num + '/' + quality + '_' + str(extract_segment[-1] + 1).zfill(3) + '.mp4'
    if os.path.exists(extract_segment_min):
        os.remove(extract_segment_min)
    if os.path.exists(extract_segment_max):
        os.remove(extract_segment_max)

    if codec == 'avc':
        bsf = 'h264_mp4toannexb'
    elif codec == 'hevc':
        bsf = 'hevc_mp4toannexb'
    else:
        raise RuntimeError
    split_list_new = []
    for item in split_list:
        cmd = 'ffmpeg -i "' + item + '" -c copy -bsf:v ' + bsf + ' -f mpegts -y "' + item + '.ts"'
        subprocess.call(cmd, shell=True)
        if os.path.exists(item):
            os.remove(item)
        split_list_new.append(item + '.ts')
    split_list = split_list_new

    if os.path.exists(out_mp4):
        os.remove(out_mp4)

    return {
        'segmant_num': segmant_num,
        'split_list': split_list,
    }
