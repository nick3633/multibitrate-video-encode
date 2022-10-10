import json


def write_encode_list(custom_encode_settings):
    ext = {
        'avc': 'h264',
        'hevc': 'h265'
    }
    for item in custom_encode_settings['video_encode_list']:
        codec = custom_encode_settings['video_encode_list'][item]['codec']
        custom_encode_settings['video_encode_list'][item]['ext'] = ext[codec]

    encode_settings = {
        "ladder": custom_encode_settings['video_encode_list'],
        "audio_ladder": {
            "atmos.eac3": {
                "codec": "eac3",
                "ext": "ec3",
                "channel": "object_based",
                'codec_settings': {
                    "Codec": "EAC3_ATMOS",
                    "Eac3AtmosSettings": {
                        "Bitrate": 768000,
                        "DynamicRangeControl": "SPECIFIED",
                        "DynamicRangeCompressionLine": "FILM_STANDARD",
                        "DynamicRangeCompressionRf": "FILM_STANDARD",
                        "SurroundExMode": "NOT_INDICATED",
                        "DownmixControl": "INITIALIZE_FROM_SOURCE",
                        "MeteringMode": "ITU_BS_1770_4",
                        "DialogueIntelligence": "ENABLED",
                        "SpeechThreshold": 15
                    }
                }
            },

            "5_1.eac3": {
                "codec": "eac3",
                "ext": "ec3",
                "channel": "5_1",
                'codec_settings': {
                    "Codec": "EAC3",
                    "Eac3Settings": {
                        "BitstreamMode": "COMPLETE_MAIN",
                        "CodingMode": "CODING_MODE_3_2",
                        "Bitrate": 640000,
                        "Dialnorm": 31,
                        "DynamicRangeCompressionLine": "FILM_STANDARD",
                        "DynamicRangeCompressionRf": "FILM_STANDARD",
                        "DcFilter": "ENABLED",
                        "LfeFilter": "ENABLED",
                        "LfeControl": "LFE",
                        "SurroundExMode": "NOT_INDICATED",
                        "StereoDownmix": "NOT_INDICATED",
                        "LtRtCenterMixLevel": -3,
                        "LtRtSurroundMixLevel": -3,
                        "LoRoCenterMixLevel": -3,
                        "LoRoSurroundMixLevel": -3,
                        "PhaseControl": "SHIFT_90_DEGREES",
                        "AttenuationControl": "NONE"
                    }
                }
            },
            "5_1.ac3": {
                "codec": "ac3",
                "ext": "ac3",
                "channel": "5_1",
                'codec_settings': {
                    "Codec": "AC3",
                    "Ac3Settings": {
                        "BitstreamMode": "COMPLETE_MAIN",
                        "CodingMode": "CODING_MODE_3_2_LFE",
                        "Bitrate": 384000,
                        "DynamicRangeCompressionLine": "FILM_STANDARD",
                        "DynamicRangeCompressionRf": "FILM_STANDARD",
                        "Dialnorm": 31,
                        "LfeFilter": "ENABLED"
                    }
                }
            },

            "2_0.eac3": {
                "codec": "eac3",
                "ext": "ec3",
                "channel": "2_0",
                'codec_settings': {
                    "Codec": "EAC3",
                    "Eac3Settings": {
                        "BitstreamMode": "COMPLETE_MAIN",
                        "CodingMode": "CODING_MODE_2_0",
                        "Bitrate": 320000,
                        "Dialnorm": 31,
                        "SurroundMode": "NOT_INDICATED",
                        "DynamicRangeCompressionLine": "FILM_STANDARD",
                        "DynamicRangeCompressionRf": "FILM_STANDARD",
                        "DcFilter": "ENABLED"
                    }
                }
            },
            "2_0.ac3": {
                "codec": "ac3",
                "ext": "ac3",
                "channel": "2_0",
                'codec_settings': {
                    "Codec": "AC3",
                    "Ac3Settings": {
                        "BitstreamMode": "COMPLETE_MAIN",
                        "CodingMode": "CODING_MODE_2_0",
                        "Bitrate": 192000,
                        "DynamicRangeCompressionLine": "FILM_STANDARD",
                        "DynamicRangeCompressionRf": "FILM_STANDARD",
                        "Dialnorm": 31
                    }
                }
            },
            "2_0.aac": {
                "codec": "aac",
                "ext": "aac",
                "channel": "2_0",
                'codec_settings': {
                    "Codec": "AAC",
                    "AacSettings": {
                        "Bitrate": 128000,
                        "CodingMode": "CODING_MODE_2_0",
                        "SampleRate": 48000,
                        "RateControlMode": "CBR",
                        "CodecProfile": "LC"
                    }
                }
            }
        }
    }

    with open('encode_settings.json', 'w') as encode_settings_file:
        encode_settings_file.write(json.dumps(encode_settings))

    return 'encode_settings.json'


def read_encode_list():
    with open('encode_settings.json', 'r') as encode_settings_file:
        encode_settings = json.loads(encode_settings_file.read())

    return encode_settings
