import os
import json

import video.dovi
import video.encode
import video.mediainfo
import video.scenecut
import video.concat


# package_dir = sys.argv[1]
def main(package_dir):
    with open(os.path.join(package_dir, 'metadata.json'), 'r') as package_file:
        package = json.loads(package_file.read())
        package_file.close()

    encode_list = {}
    video_info = {}
    for item in package:
        if item['role'] == 'video':
            video_path = os.path.join(package_dir, item['path'])
            video_mediainfo = video.mediainfo.info(video_path, item, 'sdr')

            video_info = {
                'video_path': video_path,
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

            if video_info['video_cropped_width'] >= 3840 or video_info['video_cropped_height'] >= 2160:
                encode_list['2160p.hevc'] = video_info
            if video_info['video_cropped_width'] >= 1920 or video_info['video_cropped_height'] >= 1080:
                '''encode_list['1080p.avc'] = video_info'''
                # encode_list['1080p.hevc'] = video_info

        elif item['role'] == 'video_hdr':
            video_path = os.path.join(package_dir, item['path'])
            video_mediainfo = video.mediainfo.info(video_path, item, 'hdr')
            master_display = ''
            cll = ''
            if item['hdr']['format'] == 'hdr10':
                master_display = 'G({gx},{gy})B({bx},{by})R({rx},{ry})WP({wpx},{wpy})L({lmax},{lmin})'.format(
                    gx=str(round(item['hdr']['hdr10']['mastering_display']['green_x']*50000)),
                    gy=str(round(item['hdr']['hdr10']['mastering_display']['green_y']*50000)),
                    bx=str(round(item['hdr']['hdr10']['mastering_display']['blue_x']*50000)),
                    by=str(round(item['hdr']['hdr10']['mastering_display']['blue_y']*50000)),
                    rx=str(round(item['hdr']['hdr10']['mastering_display']['red_x']*50000)),
                    ry=str(round(item['hdr']['hdr10']['mastering_display']['red_y']*50000)),
                    wpx=str(round(item['hdr']['hdr10']['mastering_display']['white_point_x']*50000)),
                    wpy=str(round(item['hdr']['hdr10']['mastering_display']['white_point_y']*50000)),
                    lmax=str(round(item['hdr']['hdr10']['mastering_display']['luminance_max']*10000)),
                    lmin=str(round(item['hdr']['hdr10']['mastering_display']['luminance_min']*10000)),
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
                encode_list['2160p.hevc.hdr'] = video_info_hdr
            elif video_info_hdr['video_cropped_width'] >= 1920 or video_info_hdr['video_cropped_height'] >= 1080:
                encode_list['1080p.hevc.hdr'] = video_info_hdr

    if ('2160p.hevc.hdr' in encode_list) and ('2160p.hevc' in encode_list):
        del encode_list['2160p.hevc']
    if ('1080p.hevc.hdr' in encode_list) and ('1080p.hevc' in encode_list):
        del encode_list['1080p.hevc']

    segment_list = video.scenecut.scenecut_list(video_info)

    for key in encode_list:
        video.concat.concat(key, video_media_info=encode_list[key], segment_list=segment_list)
