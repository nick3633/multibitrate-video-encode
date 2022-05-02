import math

h264_levels = {
    '1': {
        'mbps': 1485,
        'mb': 99,
        'maxrate': 64,
    },
    '1b': {
        'mbps': 1485,
        'mb': 99,
        'maxrate': 128,
    },
    '1.1': {
        'mbps': 3000,
        'mb': 396,
        'maxrate': 192,
    },
    '1.2': {
        'mbps': 6000,
        'mb': 396,
        'maxrate': 384,
    },
    '1.3': {
        'mbps': 11880,
        'mb': 396,
        'maxrate': 768,
    },
    '2': {
        'mbps': 11880,
        'mb': 396,
        'maxrate': 2000,
    },
    '2.1': {
        'mbps': 19800,
        'mb': 792,
        'maxrate': 4000,
    },
    '2.2': {
        'mbps': 20250,
        'mb': 1620,
        'maxrate': 4000,
    },
    '3': {
        'mbps': 40500,
        'mb': 1620,
        'maxrate': 10000,
    },
    '3.1': {
        'mbps': 108000,
        'mb': 3600,
        'maxrate': 14000,
    },
    '3.2': {
        'mbps': 216000,
        'mb': 5120,
        'maxrate': 20000,
    },
    '4': {
        'mbps': 245760,
        'mb': 8192,
        'maxrate': 20000,
    },
    '4.1': {
        'mbps': 245760,
        'mb': 8192,
        'maxrate': 50000,
    },
    '4.2': {
        'mbps': 522240,
        'mb': 8704,
        'maxrate': 50000,
    },
}
hevc_levels = {
    '1': {
        'sps': 552960,
        's': 36864,
        'maxrate': 128,
    },
    '2': {
        'sps': 3686400,
        's': 122880,
        'maxrate': 1500,
    },
    '2.1': {
        'sps': 7372800,
        's': 245760,
        'maxrate': 3000,
    },
    '3': {
        'sps': 16588800,
        's': 552960,
        'maxrate': 6000,
    },
    '3.1': {
        'sps': 33177600,
        's': 983040,
        'maxrate': 10000,
    },
    '4': {
        'sps': 66846720,
        's': 2228224,
        'maxrate': 30000,
    },
    '4.1': {
        'sps': 133693440,
        's': 2228224,
        'maxrate': 50000,
    },
    '5': {
        'sps': 267386880,
        's': 8912896,
        'maxrate': 100000,
    },
    '5.1': {
        'sps': 534773760,
        's': 8912896,
        'maxrate': 160000,
    },
    '5.2': {
        'sps': 1069547520,
        's': 8912896,
        'maxrate': 240000,
    },
}

def get_level(
        codec: str,
        codded_width: int,
        codded_height: int,
        maxrate: int,
        bufsize: int,
        profile: str,
        fps,
):
    if codec == 'avc':
        mb = math.ceil(codded_width / 16) * math.ceil(codded_height / 16)
        mbps = mb * fps
        maxrate = max(maxrate, bufsize)
        for key in h264_levels:
            level_mbps = h264_levels[key]['mbps']
            level_mb = h264_levels[key]['mb']
            level_maxrate = h264_levels[key]['maxrate']
            if profile == 'high':
                level_maxrate = level_maxrate * 1.25
            if (mbps <= level_mbps and mb <= level_mb) and maxrate <= level_maxrate:
                return key
        return '0'
    elif codec == 'hevc':
        s = codded_width * codded_height
        sps = s * fps
        maxrate = max(maxrate, bufsize)
        for key in hevc_levels:
            level_sps = hevc_levels[key]['sps']
            level_s = hevc_levels[key]['s']
            level_maxrate = hevc_levels[key]['maxrate']
            if (sps <= level_sps and s <= level_s) and maxrate <= level_maxrate:
                return key
        return '0'
    return '0'

