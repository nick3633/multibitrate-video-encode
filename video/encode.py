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
    dr = ladder[quality]['dr']
    codded_width = ladder[quality]['codded_width']
    codded_height = ladder[quality]['codded_width']
    pass1_target_rate = ladder[quality]['pass1_target_rate']
    pass2_rate_fac = ladder[quality]['pass2_rate_fac']

    if type(pass1_target_rate) == list:
        pass1_target_rate = pass1_target_rate[0] / pass1_target_rate[1]
    if type(pass2_rate_fac) == list:
        pass2_rate_fac = pass2_rate_fac[0] / pass2_rate_fac[1]

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
        res_settings = codded_width + ':-2'
    else:
        res_settings = '-2:' + codded_height

    '''build cmd base'''
    cmd_base = (
            'ffmpeg -loglevel warning -i "' + video_path + '"' +
            ' -vf "crop=' + crop_settings + ',scale=' + res_settings + '"' +
            ' -pix_fmt ' + pix_fmt + ' -strict -1 -f yuv4mpegpipe -y - | '
    )
    # p3d65 to rec2020
    # zscale=matrixin=709:transferin=smpte2084:primariesin=smpte432:matrix=2020_ncl:transfer=smpte2084:primaries=2020

    '''output file name'''
    out_avc_raw = quality + '.avc'
    out_hevc_raw = quality + '.hevc'
    out_mp4 = quality + '.mp4'
    out_state = quality + '.log'

    '''skip if completed'''
    if os.path.exists(out_avc_raw):
        return None
    if os.path.exists(out_hevc_raw):
        return None

    '''pass 1 rate control'''
    maxrate = str(round(pass1_target_rate * 1.5))
    bufsize = str(round(pass1_target_rate * 2))

    '''level and bitrate lemitation'''
    if int(codded_height) >= 2160:
        encode_level = '5.0'
        hevc_maxrate = '160000'
    elif int(codded_height) >= 1080:
        encode_level = '4.0'
        hevc_maxrate = '50000'
    else:
        encode_level = '3.1'
        hevc_maxrate = '10000'

    '''pass 1'''
    if codec == 'avc':
        cmd = [
            cmd_base +
            'x264 --log-level warning --threads 6 --demuxer y4m' +
            ' --pass 1 --slow-firstpass' +
            ' --crf 20 --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset slower --profile high --level ' + encode_level +
            ' --aq-mode 3 --aq-strength 1 --no-mbtree --no-fast-pskip --no-dct-decimate' +
            ' --sar 1:1 --stats ' + out_state + ' --output "' + out_avc_raw + '" -',

            'mp4box -add "' + out_avc_raw + '" -new "' + out_mp4 + '"'
        ]
    elif codec == 'hevc':
        cmd = [
            cmd_base +
            'x265 --log-level warning --frame-threads 4 --y4m' +
            ' --pass 1 --slow-firstpass' +
            ' --crf 20 --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset slow --profile main10 --level-idc ' + encode_level + ' --high-tier' +
            ' --repeat-headers --aud --hrd' +
            ' --aq-mode 3 --aq-strength 1 --no-cutree --no-open-gop --no-sao --pmode' +
            ' --sar 1:1 --no-info --stats ' + out_state + ' --output "' + out_hevc_raw + '" -',

            'mp4box -add "' + out_hevc_raw + '" -new "' + out_mp4 + '"'
        ]
    else:
        raise RuntimeError

    for item in cmd:
        print(item)
        subprocess.call(item, shell=True)

    '''pass 2 rate control'''
    pass1_bitrate = int(subprocess.check_output(
        'ffprobe -v error -select_streams "v:0" -show_entries "stream=bit_rate"' +
        ' -of "default=noprint_wrappers=1:nokey=1" "' + out_mp4 + '"',
        shell=True))
    bitrate = str(round(pass1_bitrate * pass2_rate_fac / 1000))
    if os.path.exists(out_mp4):
        os.remove(out_mp4)
    maxrate = str(round(pass1_target_rate * pass2_rate_fac * 1.5))
    bufsize = str(round(pass1_target_rate * pass2_rate_fac * 2))

    '''pass 2'''
    if codec == 'avc':
        cmd = [
            cmd_base +
            'x264 --log-level warning --threads 6 --demuxer y4m' +
            ' --pass 2 --slow-firstpass' +
            ' --bitrate ' + bitrate + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset slower --profile high --level ' + encode_level +
            ' --aq-mode 3 --aq-strength 1 --no-mbtree --no-fast-pskip --no-dct-decimate' +
            ' --sar 1:1 --stats ' + out_state + ' --output "' + out_avc_raw + '" -',
        ]
    elif codec == 'hevc':
        cmd = [
            cmd_base +
            'x265 --log-level warning --frame-threads 4 --y4m' +
            ' --pass 2 --slow-firstpass' +
            ' --bitrate ' + bitrate + ' --vbv-maxrate ' + maxrate + ' --vbv-bufsize ' + bufsize +
            ' --preset slow --profile main10 --level-idc ' + encode_level + ' --high-tier' +
            ' --repeat-headers --aud --hrd' +
            ' --aq-mode 3 --aq-strength 1 --no-cutree --no-open-gop --no-sao --pmode' +
            ' --sar 1:1 --no-info --stats ' + out_state + ' --output "' + out_hevc_raw + '" -',
        ]
    else:
        raise RuntimeError

    for item in cmd:
        print(item)
        subprocess.call(item, shell=True)
    if os.path.exists(out_state):
        os.remove(out_state)
