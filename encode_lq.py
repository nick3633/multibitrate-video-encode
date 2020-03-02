import subprocess
import os


def avc_enc(video_input, res, fps_denominator, fps_numerator, filter_res_type, pix_convert, in_dr):
    if os.path.exists(res + '-avc-pass2.mp4'):
        return None

    fps = (fps_denominator / fps_numerator)
    keyint = fps * 5  # get keyint

    filter_res = None
    pass1_rc = None
    pass2_r_fac = None
    pass2_rc = None
    if res == '1080p':
        crf = '23'
        filter_res_w = '1920:-2'
        filter_res_h = '-2:1080'
        profile_v = 'high'
        pass1_maxrate = 4000
        pass2_r_fac = 1
        pass2_rc = ' -profile:v high -level 4.0 '
    elif res == '720p':
        crf = '23'
        filter_res_w = '1280:-2'
        filter_res_h = '-2:720'
        profile_v = 'main'
        pass1_maxrate = 16000 / 9
        pass2_r_fac = 45 / 32
        pass2_rc = ' -profile:v main -level 3.1 '
    elif res == '480p':
        crf = '23'
        filter_res_w = '854:-2'
        filter_res_h = '-2:480'
        profile_v = 'main'
        pass1_maxrate = 64000 / 81
        pass2_r_fac = 405 / 256
        pass2_rc = ' -profile:v main -level 3.0 '
    elif res == '360p':
        crf = '23'
        filter_res_w = '640:-2'
        filter_res_h = '-2:360'
        profile_v = 'main'
        pass1_maxrate = 4000 / 9
        pass2_r_fac = 9 / 8
        pass2_rc = ' -profile:v main -level 3.0 '
    elif res == '240p':
        crf = '23'
        filter_res_w = '426:-2'
        filter_res_h = '-2:240'
        profile_v = 'main'
        pass1_maxrate = 16000 / 81
        pass2_r_fac = 81 / 80
        pass2_rc = ' -profile:v main -level 2.1 '
    elif res == '144p':
        crf = '23'
        filter_res_w = '256:-2'
        filter_res_h = '-2:144'
        profile_v = 'main'
        pass1_maxrate = 640 / 9
        pass2_r_fac = 9 / 8
        pass2_rc = ' -profile:v main -level 1.2 '

    if filter_res_type == 'w':
        filter_res = filter_res_w
    elif filter_res_type == 'h':
        filter_res = filter_res_h

    pass1_bufsize = str(round(pass1_maxrate * 4)) + 'K'
    pass1_maxrate = str(round(pass1_maxrate)) + 'K'

    hdr_to_sdr = ''
    if in_dr == 'HDR 10':
        hdr_to_sdr = ',scale=-1:-1:in_color_matrix=bt2020,format=rgb48,lut3d=bt2020_to_bt709_example.cube,scale=-1:-1:out_color_matrix=bt709'

    enc_cmd = ('ffmpeg -i "' + video_input +
               '" -vf "fps=fps=' + str(fps_denominator) + '/' + str(
                fps_numerator) + ',scale=' + filter_res + hdr_to_sdr + ',' + pix_convert + '" -color_primaries 1 -color_trc 1 -colorspace 1 -color_range 1 ' +
               ' -c:v libx264 -preset medium -pass 1 ' +
               ' -crf ' + crf + ' -maxrate ' + pass1_maxrate + ' -bufsize ' + pass1_bufsize + ' -profile:v ' + profile_v +
               ' -g ' + str(round(keyint)) + ' -keyint_min ' + str(round(keyint)) + ' -sc_threshold 0' +
               ' -x264-params "aq-mode=1" ' +
               ' -an -passlogfile ' + res + '-avc-2pass ' + res + '-avc-pass1.mp4 ')

    print(enc_cmd)
    subprocess.call(enc_cmd, shell=True)

    pass1_bitrate = int(subprocess.check_output(
        'ffprobe -v error -select_streams "v:0" -show_entries "stream=bit_rate" -of "default=noprint_wrappers=1:nokey=1" ' + res + '-avc-pass1.mp4',
        shell=True))
    pass2_bitrate = pass1_bitrate / 1000 * pass2_r_fac
    pass2_maxrate = str(round(pass2_bitrate * 2)) + 'K'
    pass2_bufsize = str(round(pass2_bitrate * 2)) + "K"
    pass2_bitrate = str(round(pass2_bitrate)) + "K"

    if os.path.exists("" + res + "-avc-pass1.mp4"):
        os.remove("" + res + "-avc-pass1.mp4")

    enc_cmd = ('ffmpeg -i "' + video_input +
               '" -vf "fps=fps=' + str(fps_denominator) + '/' + str(
                fps_numerator) + ',scale=' + filter_res + hdr_to_sdr + ',' + pix_convert + '" -color_primaries 1 -color_trc 1 -colorspace 1 -color_range 1 ' +
               '-c:v libx264 -preset medium -pass 2 ' +
               '-b:v ' + pass2_bitrate + ' -maxrate ' + pass2_maxrate + pass2_rc + ' -bufsize ' + pass2_bufsize + ' ' +
               '-g ' + str(round(keyint)) + ' -keyint_min ' + str(round(keyint)) + ' -sc_threshold 0' +
               ' -x264-params "aq-mode=1" ' +
               ' -map_metadata -1 -an -passlogfile ' + res + '-avc-2pass ' + res + '-avc-pass2.mp4')

    print(enc_cmd)
    subprocess.call(enc_cmd, shell=True)

    if os.path.exists(res + "-avc-2pass-0.log"):
        os.remove(res + "-avc-2pass-0.log")
    if os.path.exists(res + "-avc-2pass-0.log.mbtree"):
        os.remove(res + "-avc-2pass-0.log.mbtree")


def hevc_enc(video_input, res, fps_denominator, fps_numerator, filter_res_type, pix_convert, in_dr):
    if os.path.exists(res + '-hevc-pass2.mp4'):
        return None

    fps = (fps_denominator / fps_numerator)
    keyint = fps * 5  # get keyint

    filter_res = None
    pass1_rc = None
    pass2_r_fac = None
    pass2_rc = None

    if res == '2160p':
        crf = '23'
        filter_res_w = '3840:-2'
        filter_res_h = '-2:2160'
        pass1_maxrate = 16000
        pass2_r_fac = 1 * (5 / 4) * 0.5
        pass2_level = '5.0'
    elif res == '1440p':
        crf = '23'
        filter_res_w = '2560:-2'
        filter_res_h = '-2:1440'
        pass1_maxrate = 64000 / 9
        pass2_r_fac = 1 * (9 / 8) * (2 / 3)
        pass2_level = '5.0'
    elif res == '1080p':
        crf = '23'
        filter_res_w = '1920:-2'
        filter_res_h = '-2:1080'
        pass1_maxrate = 4000
        pass2_r_fac = 1 * 0.75
        pass2_level = '4.0'
    elif res == '720p':
        crf = '23'
        filter_res_w = '1280:-2'
        filter_res_h = '-2:720'
        pass1_maxrate = 16000 / 9
        pass2_r_fac = (45 / 32) * (5 / 6)
        pass2_level = '3.1'
    elif res == '480p':
        crf = '23'
        filter_res_w = '854:-2'
        filter_res_h = '-2:480'
        pass1_maxrate = 64000 / 81
        pass2_r_fac = (405 / 256) * (8 / 9)
        pass2_level = '3.0'
    elif res == '360p':
        crf = '23'
        filter_res_w = '640:-2'
        filter_res_h = '-2:360'
        pass1_maxrate = 4000 / 9
        pass2_r_fac = (9 / 8) * (11 / 12)
        pass2_level = '3.0'
    elif res == '240p':
        crf = '23'
        filter_res_w = '426:-2'
        filter_res_h = '-2:240'
        pass1_maxrate = 16000 / 81
        pass2_r_fac = (81 / 80) * (17 / 18)
        pass2_level = '2.1'
    elif res == '144p':
        crf = '23'
        filter_res_w = '256:-2'
        filter_res_h = '-2:144'
        pass1_maxrate = 640 / 9
        pass2_r_fac = (9 / 8) * (29 / 30)
        pass2_level = '2.0'

    if filter_res_type == 'w':
        filter_res = filter_res_w
    elif filter_res_type == 'h':
        filter_res = filter_res_h

    hdr_to_sdr = ''
    if in_dr == 'HDR 10':
        hdr_to_sdr = ',scale=-1:-1:in_color_matrix=bt2020,format=rgb48le,lut3d=bt2020_to_bt709_example.cube,scale=-1:-1:out_color_matrix=bt709'

    pass1_bufsize = str(round(pass1_maxrate * 4)) + 'K'
    pass1_maxrate = str(round(pass1_maxrate)) + 'K'

    enc_cmd = ('ffmpeg -i "' + video_input +
               '" -vf "fps=fps=' + str(fps_denominator) + '/' + str(
                fps_numerator) + ',scale=' + filter_res + hdr_to_sdr + ',' + pix_convert + '" -color_primaries 1 -color_trc 1 -colorspace 1 -color_range 1 ' +
               ' -c:v libx265 -preset medium ' +
               ' -crf ' + crf + ' -maxrate ' + pass1_maxrate + ' -bufsize ' + pass1_bufsize +
               ' -x265-params "no-info=1:aq-mode=1:keyint=' + str(round(keyint)) + ':min-keyint=' + str(
                round(keyint)) + ':no-scenecut=1:pass=1:stats=' + res + '-hevc-2pass.log" ' +
               ' -an ' + res + '-hevc-pass1.mp4 ')

    print(enc_cmd)
    subprocess.call(enc_cmd, shell=True)

    pass1_bitrate = int(subprocess.check_output(
        'ffprobe -v error -select_streams "v:0" -show_entries "stream=bit_rate" -of "default=noprint_wrappers=1:nokey=1" ' + res + '-hevc-pass1.mp4',
        shell=True))
    pass2_bitrate = pass1_bitrate / 1000 * pass2_r_fac
    pass2_maxrate = str(round(pass2_bitrate * 2)) + 'K'
    pass2_bufsize = str(round(pass2_bitrate * 2)) + "K"
    pass2_bitrate = str(round(pass2_bitrate)) + "K"

    if os.path.exists("" + res + "-hevc-pass1.mp4"):
        os.remove("" + res + "-hevc-pass1.mp4")

    enc_cmd = ('ffmpeg -i "' + video_input +
               '" -vf "fps=fps=' + str(fps_denominator) + '/' + str(
                fps_numerator) + ',scale=' + filter_res + hdr_to_sdr + ',' + pix_convert + '" -color_primaries 1 -color_trc 1 -colorspace 1 -color_range 1 ' +
               '-c:v libx265 -preset medium ' +
               '-b:v ' + pass2_bitrate + ' -maxrate ' + pass2_maxrate + ' -bufsize ' + pass2_bufsize + ' ' +
               '-x265-params "no-info=1:aq-mode=1:level-idc=' + pass2_level + ':keyint=' + str(
                round(keyint)) + ':min-keyint=' + str(
                round(keyint)) + ':no-scenecut=1:pass=2:stats=' + res + '-hevc-2pass.log" ' +
               ' -map_metadata -1 -an ' + res + '-hevc-pass2.mp4 ')

    print(enc_cmd)
    subprocess.call(enc_cmd, shell=True)

    if os.path.exists(res + "-hevc-2pass.log"):
        os.remove(res + "-hevc-2pass.log")
    if os.path.exists(res + "-hevc-2pass.log.cutree"):
        os.remove(res + "-hevc-2pass.log.cutree")
