from xml.dom import minidom
from encode_lq import *


def video_processor_lq(video_input: str):
    hdr = 'SDR'
    if not (os.path.exists(video_input + ".xml")):
        subprocess.call(
            'ffprobe -v quiet -print_format xml -show_entries stream=width,height,r_frame_rate,pix_fmt,color_space,color_transfer ' + video_input + ' > mediainfo.xml',
            shell=True)
        mediainfo_xml = minidom.parse('mediainfo.xml')
    else:
        mediainfo_xml = minidom.parse(video_input + ".xml")

    stream = mediainfo_xml.getElementsByTagName('stream')
    input_fps = stream[0].attributes['r_frame_rate'].value
    input_width = int(stream[0].attributes['width'].value)
    input_height = int(stream[0].attributes['height'].value)
    input_pix_fmt = stream[0].attributes['pix_fmt'].value
    eightbit_pix_fmts = ['yuv420p', 'yuv422p', 'yuv444p', 'rgb24']

    try:
        if stream[0].attributes['color_space'].value == 'bt2020nc' and stream[0].attributes[
            'color_transfer'].value == 'smpte2084':
            hdr = 'HDR 10'
    except KeyError:
        print('no color space info')

    if input_pix_fmt in eightbit_pix_fmts:
        pix_convert = 'format=yuv420p'
    else:
        pix_convert = 'format=rgb48le,format=rgb24,format=yuv420p'

    print(pix_convert)

    fps = input_fps.split('/')
    fps_denominator = int(fps[0])
    fps_denominator_low = fps_denominator
    fps_numerator = int(fps[1])

    encode_fps = fps_denominator / fps_numerator
    if encode_fps > 30:
        fps_denominator_low = int(fps_denominator / 2)

    print(fps_denominator)
    print(fps_denominator_low)
    print(fps_numerator)

    if (input_width / input_height) >= (16 / 9):
        r = 'w'
        input_side = input_width
    else:
        r = 'h'
        input_side = input_height

    if input_width >= 640 or input_height >= 360:
        avc_enc(video_input, '360p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
        hevc_enc(video_input, '360p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    if input_width >= 854 or input_height >= 480:
        avc_enc(video_input, '480p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
        hevc_enc(video_input, '480p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    if input_width >= 1280 or input_height >= 720:
        avc_enc(video_input, '720p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
        hevc_enc(video_input, '720p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    if input_width >= 1920 or input_height >= 1080:
        avc_enc(video_input, '1080p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
        hevc_enc(video_input, '1080p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    if input_width >= 2560 or input_height >= 1440:
        hevc_enc(video_input, '1440p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    if input_width >= 3840 or input_height >= 2160:
        hevc_enc(video_input, '2160p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    avc_enc(video_input, '240p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
    hevc_enc(video_input, '240p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)

    avc_enc(video_input, '144p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
    hevc_enc(video_input, '144p', fps_denominator_low, fps_numerator, r, pix_convert, hdr)
