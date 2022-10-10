import os
import json
import subprocess

import encode_list
import default_encode_settings
import video.dovi
import video.encode
import video.encode_traditional
import video.mediainfo
import video.scenecut
import video.concat
import audio.mediainfo
import audio.encode


def main(package_dir):
    """load metadata and encode settings"""
    package_dir = os.path.normpath(package_dir)
    with open(os.path.join(package_dir, 'metadata.json'), 'r') as package_file:
        package = json.loads(package_file.read())
        package_file.close()

    encode_settings_path = os.path.join(package_dir, 'encode_settings.json')
    if os.path.exists(encode_settings_path):
        old_encode_settings = json.loads(default_encode_settings.encode_settings)
        with open(os.path.join(package_dir, 'encode_settings.json'), 'r') as encode_settings_file:
            custom_encode_settings = json.loads(encode_settings_file.read())
        custom_encode_settings = {**old_encode_settings, **custom_encode_settings}
    else:
        custom_encode_settings = json.loads(default_encode_settings.encode_settings)

    encode_list.write_encode_list(custom_encode_settings)
    ladder = encode_list.read_encode_list()
    v_ladder = ladder['ladder']
    # a_ladder = ladder['audio_ladder']

    chunked_encoding = custom_encode_settings['video_other_settings']['chunked_encoding']
    highest_res_only = custom_encode_settings['video_other_settings']['sdr_highest_res_only']
    hdr_highest_res_only = custom_encode_settings['video_other_settings']['hdr_highest_res_only']
    replace_sdr_with_hdr = custom_encode_settings['video_other_settings']['replace_sdr_with_hdr']
    hls_compatible = custom_encode_settings['video_other_settings']['hls_compatible']
    hls_compatible_keyint_second = None
    if hls_compatible is True:
        hls_compatible_keyint_second = \
            custom_encode_settings['video_other_settings']['hls_compatible_settings']['keyint_second']

    """create final encode list"""
    video_encode_list = {}
    video_hdr_encode_list = {}
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
                'hls_compatible': hls_compatible,
                'hls_compatible_keyint_second': hls_compatible_keyint_second,
            }

            for v_ladder_item in v_ladder:
                item_width = int(v_ladder[v_ladder_item]['codded_width'])
                item_height = int(v_ladder[v_ladder_item]['codded_height'])
                item_dr = v_ladder[v_ladder_item]['dr']
                if video_info['video_cropped_width'] >= item_width or video_info['video_cropped_height'] >= item_height:
                    if item_dr == 'sdr':
                        video_encode_list[v_ladder_item] = video_info

            if ('ignore_audio' in item and 'ignore_audio' == False) or ('ignore_audio' not in item):
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
                'hls_compatible': hls_compatible,
                'hls_compatible_keyint_second': hls_compatible_keyint_second,
            }
            for v_ladder_item in v_ladder:
                item_width = int(v_ladder[v_ladder_item]['codded_width'])
                item_height = int(v_ladder[v_ladder_item]['codded_height'])
                item_dr = v_ladder[v_ladder_item]['dr']
                if video_info_hdr['video_cropped_width'] >= item_width or \
                        video_info_hdr['video_cropped_height'] >= item_height:
                    if item_dr == 'hdr':
                        video_hdr_encode_list[v_ladder_item] = video_info_hdr

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

    """edit encode list"""
    if highest_res_only is True:
        video_encode_list_sort = {}
        res_list = []
        for item in video_encode_list:
            total_res = int(v_ladder[item]['codded_width']) * int(v_ladder[item]['codded_height'])
            res_list.append(total_res)
        res_list.sort(reverse=True)
        for item in video_encode_list:
            total_res = int(v_ladder[item]['codded_width']) * int(v_ladder[item]['codded_height'])
            if total_res == res_list[0]:
                video_encode_list_sort[item] = video_encode_list[item]
                break
        video_encode_list = video_encode_list_sort

    if hdr_highest_res_only is True:
        video_hdr_encode_list_sort = {}
        res_list = []
        for item in video_hdr_encode_list:
            total_res = int(v_ladder[item]['codded_width']) * int(v_ladder[item]['codded_height'])
            res_list.append(total_res)
        res_list.sort(reverse=True)
        for item in video_hdr_encode_list:
            total_res = int(v_ladder[item]['codded_width']) * int(v_ladder[item]['codded_height'])
            if total_res == res_list[0]:
                video_hdr_encode_list_sort[item] = video_hdr_encode_list[item]
                break
        video_hdr_encode_list = video_hdr_encode_list_sort

    if replace_sdr_with_hdr is True:
        del_list = []
        for item in video_hdr_encode_list:
            total_res = int(v_ladder[item]['codded_width']) * int(v_ladder[item]['codded_height'])
            codec = v_ladder[item]['codec']
            for item_sdr in video_encode_list:
                total_res_sdr = int(v_ladder[item_sdr]['codded_width']) * int(v_ladder[item_sdr]['codded_height'])
                codec_sdr = v_ladder[item_sdr]['codec']
                if total_res == total_res_sdr and codec == codec_sdr:
                    del_list.append(item_sdr)
        for key in del_list:
            del video_encode_list[key]

    video_encode_list = {**video_encode_list, **video_hdr_encode_list}
    print(json.dumps(video_encode_list, indent=2))

    """encode video"""
    if chunked_encoding is True:
        segment_list = video.scenecut.scenecut_list(video_info)
        for key in video_encode_list:
            video.concat.concat(key, video_media_info=video_encode_list[key], segment_list=segment_list)
    else:
        for key in video_encode_list:
            video.encode_traditional.encode(key, video_media_info=video_encode_list[key])

    """encode audio"""
    if ('5_1.eac3' in audio_encode_list) and ('2_0.eac3' in audio_encode_list):
        del audio_encode_list['2_0.eac3']
    if ('5_1.ac3' in audio_encode_list) and ('2_0.ac3' in audio_encode_list):
        del audio_encode_list['2_0.ac3']

    reuse_audio_info = {
        'in_bucket_name': '',
        'out_bucket_name': '',
        'tmp_audio_file': ''
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
    '''if os.path.exists('encode_settings.json'):
        os.remove('encode_settings.json')'''
