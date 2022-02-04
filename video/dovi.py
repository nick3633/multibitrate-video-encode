import xml.etree.ElementTree as ET


def metadata(dovi_metadata):
    tree = ET.parse(dovi_metadata)
    root = tree.getroot()

    mastering_display = root.find('Outputs/Output/Video/Track/PluginNode/DolbyEDR/Characteristics/MasteringDisplay')
    red = mastering_display.find('Primaries/Red').text
    green = mastering_display.find('Primaries/Red').text
    blue = mastering_display.find('Primaries/Red').text
    white_point = mastering_display.find('WhitePoint').text

    master_display = 'G({gx},{gy})B({bx},{by})R({rx},{ry})WP({wpx},{wpy})L({lmax},{lmin})'.format(
        gx=str(int(green.split(',')[0]) * 50000),
        gy=str(int(green.split(',')[1]) * 50000),
        bx=str(int(blue.split(',')[0]) * 50000),
        by=str(int(blue.split(',')[1]) * 50000),
        rx=str(int(red.split(',')[0]) * 50000),
        ry=str(int(red.split(',')[1]) * 50000),
        wpx=str(int(white_point.split(',')[0]) * 50000),
        wpy=str(int(white_point.split(',')[1]) * 50000),
        lmax=str(int(mastering_display.find('PeakBrightness').text) * 10000),
        lmin=str(int(mastering_display.find('MinimumBrightness').text) * 10000),
    )
    cll = '"{cll},{fall}"'.format(
        cll=root.find('Outputs/Output/Video/Track/Level6/MaxCLL').text,
        fall=root.find('Outputs/Output/Video/Track/Level6/MaxFALL').text,
    )

    return {
        'master_display': master_display,
        'cll': cll,
    }
