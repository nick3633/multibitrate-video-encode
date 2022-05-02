import os
import json
import subprocess

import encode_settings
import video.dovi
import video.encode
import video.encode_traditional
import video.mediainfo
import video.scenecut
import video.concat
import audio.mediainfo
import audio.encode


v_ladder = encode_settings.encode_settings['ladder']
a_ladder = encode_settings.encode_settings['audio_ladder']


# package_dir = sys.argv[1]
def main(package_dir, chunked_encoding=True):
    package_dir = os.path.normpath(package_dir)
    with open(os.path.join(package_dir, 'metadata.json'), 'r') as package_file:
        package = json.loads(package_file.read())
        package_file.close()

    video_encode_list = {}
    audio_encode_list = {}
    video_info = {}
    for item in package['asset']:
        if item['role'] == 'video':
            video_path = os.path.join(package_dir, item['path'])
            video_mediainfo = video.mediainfo.info(video_path, item, 'sdr')

            video_info = {
                'video_path': video_path,
                'video_lang': item['language'],
                'video_crop_top': item['crop']['top'],
                'video_crop_bottom': item['crop']['bottom'],
                'video_crop_left': item['crop']['left'],
                'video_crop_right': item['crop']['right'],
                'video_fps': video_mediainfo['video_fps'],
                'video_frame_count': video_mediainfo['video_frame_count'],
                'video_width': video_mediainfo['video_width'],
                'video_height': video_mediainfo['video_height'],
                'video_cropped_width': video_mediainfo['video_cropped_width'],
                'video_cropped_height': video_mediainfo['video_cropped_height'],
            }

            if video_info['video_cropped_width'] >= 854 or video_info['video_cropped_height'] >= 480:
                video_encode_list['480p.avc'] = video_info
                video_encode_list['480p.hevc'] = video_info
            if video_info['video_cropped_width'] >= 1920 or video_info['video_cropped_height'] >= 1080:
                video_encode_list['1080p.avc'] = video_info
                video_encode_list['1080p.hevc'] = video_info
            if video_info['video_cropped_width'] >= 3840 or video_info['video_cropped_height'] >= 2160:
                video_encode_list['2160p.hevc'] = video_info

            if ('ignore_audio' in item and 'ignore_audio' is False) or ('ignore_audio' not in item):
                audio_mediainfo = audio.mediainfo.info(video_path)

                audio_info = {
                    'audio_path': video_path,
                    'audio_lang': item['language'],
                    'audio_tracks': audio_mediainfo,
                }

                if '5_1' in audio_mediainfo:
                    audio_encode_list['5_1.eac3'] = audio_info
                    audio_encode_list['5_1.ac3'] = audio_info
                    audio_info['audio_loudness'] = item['loudness']
                if '2_0' in audio_mediainfo:
                    audio_encode_list['2_0.eac3'] = audio_info
                    audio_encode_list['2_0.ac3'] = audio_info
                    audio_encode_list['2_0.aac'] = audio_info
                    audio_info['audio_loudness'] = item['loudness']

        elif item['role'] == 'video_hdr':
            video_path = os.path.join(package_dir, item['path'])
            video_mediainfo = video.mediainfo.info(video_path, item, 'hdr')
            master_display = ''
            cll = ''
            if item['hdr']['format'] == 'hdr10':
                master_display = 'G({gx},{gy})B({bx},{by})R({rx},{ry})WP({wpx},{wpy})L({lmax},{lmin})'.format(
                    gx=str(round(item['hdr']['hdr10']['mastering_display']['green_x'] * 50000)),
                    gy=str(round(item['hdr']['hdr10']['mastering_display']['green_y'] * 50000)),
                    bx=str(round(item['hdr']['hdr10']['mastering_display']['blue_x'] * 50000)),
                    by=str(round(item['hdr']['hdr10']['mastering_display']['blue_y'] * 50000)),
                    rx=str(round(item['hdr']['hdr10']['mastering_display']['red_x'] * 50000)),
                    ry=str(round(item['hdr']['hdr10']['mastering_display']['red_y'] * 50000)),
                    wpx=str(round(item['hdr']['hdr10']['mastering_display']['white_point_x'] * 50000)),
                    wpy=str(round(item['hdr']['hdr10']['mastering_display']['white_point_y'] * 50000)),
                    lmax=str(round(item['hdr']['hdr10']['mastering_display']['luminance_max'] * 10000)),
                    lmin=str(round(item['hdr']['hdr10']['mastering_display']['luminance_min'] * 10000)),
                )
                cll = '{cll},{fall}'.format(
                    cll=str(item['hdr']['hdr10']['content_lightlevel']['max']),
                    fall=str(item['hdr']['hdr10']['content_lightlevel']['max_frame_avg']),
                )
            elif item['hdr']['format'] == 'dolby_vision':
                dovi_metadata_path = os.path.join(package_dir, item['hdr']['dolby_vision']['metadata'])
                hdr10_metadata = video.dovi.metadata(dovi_metadata_path)
                master_display = hdr10_metadata['master_display']
                cll = hdr10_metadata['cll']

            video_info_hdr = {
                'video_path': video_path,
                'video_lang': item['language'],
                'video_crop_top': item['crop']['top'],
                'video_crop_bottom': item['crop']['bottom'],
                'video_crop_left': item['crop']['left'],
                'video_crop_right': item['crop']['right'],
                'video_fps': video_mediainfo['video_fps'],
                'video_frame_count': video_mediainfo['video_frame_count'],
                'video_width': video_mediainfo['video_width'],
                'video_height': video_mediainfo['video_height'],
                'video_cropped_width': video_mediainfo['video_cropped_width'],
                'video_cropped_height': video_mediainfo['video_cropped_height'],
                'video_master_display': master_display,
                'video_cll': cll,
                'video_colour_primaries': video_mediainfo['video_colour_primaries'],
                'video_transfer_characteristics': video_mediainfo['video_transfer_characteristics'],
                'video_matrix_coefficients': video_mediainfo['video_matrix_coefficients'],
            }
            if video_info_hdr['video_cropped_width'] >= 3840 or video_info_hdr['video_cropped_height'] >= 2160:
                video_encode_list['2160p.hevc.hdr'] = video_info_hdr
            elif video_info_hdr['video_cropped_width'] >= 1920 or video_info_hdr['video_cropped_height'] >= 1080:
                video_encode_list['1080p.hevc.hdr'] = video_info_hdr

        elif item['role'] == 'audio' and item['primary_audio'] is True:
            mov_path = os.path.join(package_dir, item['path'])
            audio_mediainfo = audio.mediainfo.info(mov_path)

            audio_info = {
                'audio_path': mov_path,
                'audio_lang': item['language'],
                'audio_tracks': audio_mediainfo,
            }

            if '5_1' in audio_mediainfo:
                audio_encode_list['5_1.eac3'] = audio_info
                audio_encode_list['5_1.ac3'] = audio_info
                audio_info['audio_loudness'] = item['loudness']
            if '2_0' in audio_mediainfo:
                audio_encode_list['2_0.eac3'] = audio_info
                audio_encode_list['2_0.ac3'] = audio_info
                audio_encode_list['2_0.aac'] = audio_info
                audio_info['audio_loudness'] = item['loudness']

        elif item['role'] == 'audio_object_based':
            adm_bwf_path = os.path.join(package_dir, item['path'])
            audio_info = {
                'audio_path': adm_bwf_path,
                'audio_lang': item['language'],
                'audio_loudness': 'not_applicable'
            }
            audio_encode_list['atmos.eac3'] = audio_info

    print(json.dumps(video_encode_list, indent=2))
    print(json.dumps(audio_encode_list, indent=2))

    # video
    if ('1080p.hevc.hdr' in video_encode_list) and ('1080p.hevc' in video_encode_list):
        del video_encode_list['1080p.hevc']
    if ('2160p.hevc.hdr' in video_encode_list) and ('2160p.hevc' in video_encode_list):
        del video_encode_list['2160p.hevc']

    if chunked_encoding is True:
        segment_list = video.scenecut.scenecut_list(video_info)
        for key in video_encode_list:
            video.concat.concat(key, video_media_info=video_encode_list[key], segment_list=segment_list)
    else:
        for key in video_encode_list:
            video.encode_traditional.encode(key, video_media_info=video_encode_list[key])

    # audio
    if ('5_1.eac3' in audio_encode_list) and ('2_0.eac3' in audio_encode_list):
        del audio_encode_list['2_0.eac3']
    if ('5_1.ac3' in audio_encode_list) and ('2_0.ac3' in audio_encode_list):
        del audio_encode_list['2_0.ac3']

    reuse_audio_info = {
        'in_bucket_name': None,
        'out_bucket_name': None,
        'tmp_audio_file': None
    }
    for key in audio_encode_list:
        reuse_audio_info = audio.encode.encode(key, audio_encode_list[key], reuse_audio_info)

    cmd = []
    if reuse_audio_info['in_bucket_name']:
        cmd.append('aws s3 rm s3://' + reuse_audio_info['in_bucket_name'] + '/ --recursive --include "*"')
        cmd.append('aws s3api delete-bucket --bucket "' + reuse_audio_info['in_bucket_name'] + '"')
    if reuse_audio_info['out_bucket_name']:
        cmd.append('aws s3 rm s3://' + reuse_audio_info['out_bucket_name'] + '/ --recursive --include "*"')
        cmd.append('aws s3api delete-bucket --bucket "' + reuse_audio_info['out_bucket_name'] + '"')
    for item in cmd:
        subprocess.call(item, shell=True)
    if reuse_audio_info['tmp_audio_file'] and os.path.exists(reuse_audio_info['tmp_audio_file']):
        os.remove(reuse_audio_info['tmp_audio_file'])

    # mux
    videofile = ''
    if '2160p.hevc.hdr' in video_encode_list:
        videofile = '2160p.hevc.hdr.' + v_ladder['2160p.hevc.hdr']['ext']
    elif '2160p.hevc' in video_encode_list:
        videofile = '2160p.hevc.' + v_ladder['2160p.hevc']['ext']
    elif '1080p.hevc.hdr' in video_encode_list:
        videofile = '1080p.hevc.hdr.' + v_ladder['1080p.hevc.hdr']['ext']
    elif '1080p.hevc' in video_encode_list:
        videofile = '1080p.hevc.' + v_ladder['1080p.hevc']['ext']
    elif '1080p.avc' in video_encode_list:
        videofile = '1080p.avc.' + v_ladder['1080p.avc']['ext']

    audiofile_eac3 = ''
    audiofile_eac3_info = {}
    audio_file_ac3 = ''
    audio_file_ac3_info = {}
    if 'atmos.eac3' in audio_encode_list and '5_1.ac3' in audio_encode_list:
        audiofile_eac3 = a_ladder['atmos.eac3']['channel'] + '.' + a_ladder['atmos.eac3']['codec'] + '.' + a_ladder['atmos.eac3']['ext']
        audiofile_eac3_info = audio_encode_list['atmos.eac3']
        audio_file_ac3 = a_ladder['5_1.ac3']['channel'] + '.' + a_ladder['5_1.ac3']['codec'] + '.' + a_ladder['5_1.ac3']['ext']
        audio_file_ac3_info = audio_encode_list['5_1.ac3']
    elif '5_1.eac3' in audio_encode_list and '5_1.ac3' in audio_encode_list:
        audiofile_eac3 = a_ladder['5_1.eac3']['channel'] + '.' + a_ladder['5_1.eac3']['codec'] + '.' + a_ladder['5_1.eac3']['ext']
        audiofile_eac3_info = audio_encode_list['5_1.eac3']
        audio_file_ac3 = a_ladder['5_1.ac3']['channel'] + '.' + a_ladder['5_1.ac3']['codec'] + '.' + a_ladder['5_1.ac3']['ext']
        audio_file_ac3_info = audio_encode_list['5_1.ac3']
    elif '2_0.eac3' in audio_encode_list and '2_0.ac3' in audio_encode_list:
        audiofile_eac3 = a_ladder['2_0.eac3']['channel'] + '.' + a_ladder['2_0.eac3']['codec'] + '.' + a_ladder['2_0.eac3']['ext']
        audiofile_eac3_info = audio_encode_list['2_0.eac3']
        audio_file_ac3 = a_ladder['2_0.ac3']['channel'] + '.' + a_ladder['2_0.ac3']['codec'] + '.' + a_ladder['2_0.ac3']['ext']
        audio_file_ac3_info = audio_encode_list['2_0.ac3']

    cmd = [
        'mkvmerge -o video.mkv --title "' + package['title'] + '"' +
        ' "' + videofile + '"' +
        ' --language "0:' + audiofile_eac3_info['audio_lang'] + '" "' + audiofile_eac3 + '"' +
        ' --language "0:' + audio_file_ac3_info['audio_lang'] + '" "' + audio_file_ac3 + '"'
    ]
    if not os.path.exists('video.mkv'):
        print(cmd[0])
        subprocess.call(cmd[0], shell=True)
