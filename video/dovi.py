import xml.etree.ElementTree as ET

import util


def metadata(dovi_metadata):
    tree = ET.parse(dovi_metadata)
    root = tree.getroot()

    mastering_display = root.find('Outputs/Output/Video/Track/PluginNode/DolbyEDR/Characteristics/MasteringDisplay')
    red = mastering_display.find('Primaries/Red').text
    green = mastering_display.find('Primaries/Green').text
    blue = mastering_display.find('Primaries/Blue').text
    white_point = mastering_display.find('WhitePoint').text

    master_display = 'G({gx},{gy})B({bx},{by})R({rx},{ry})WP({wpx},{wpy})L({lmax},{lmin})'.format(
        gx=str(util.math_round(float(green.split(',')[0]) * 50000)),
        gy=str(util.math_round(float(green.split(',')[1]) * 50000)),
        bx=str(util.math_round(float(blue.split(',')[0]) * 50000)),
        by=str(util.math_round(float(blue.split(',')[1]) * 50000)),
        rx=str(util.math_round(float(red.split(',')[0]) * 50000)),
        ry=str(util.math_round(float(red.split(',')[1]) * 50000)),
        wpx=str(util.math_round(float(white_point.split(',')[0]) * 50000)),
        wpy=str(util.math_round(float(white_point.split(',')[1]) * 50000)),
        lmax=str(util.math_round(float(mastering_display.find('PeakBrightness').text) * 10000)),
        lmin=str(util.math_round(float(mastering_display.find('MinimumBrightness').text) * 10000)),
    )
    cll = '{cll},{fall}'.format(
        cll=root.find('Outputs/Output/Video/Track/Level6/MaxCLL').text,
        fall=root.find('Outputs/Output/Video/Track/Level6/MaxFALL').text,
    )

    return {
        'master_display': master_display,
        'cll': cll,
    }
