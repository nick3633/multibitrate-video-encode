encode_settings = {
    "ladder": {
        "2160p.hevc": {
            "codec": "hevc",
            "ext": "265",
            "dr": "sdr",
            "codded_width": "3840",
            "codded_height": "2160",
            "maxrate": "30000",
            "bufsize": "40000",
            "encode_speed": "slower",
            "encode_profile": "main10",
            "encode_level": "5.1",
            "encode_extra_settings": " --bframes 8 --qg-size 32 --no-rc-grain --psy-rd 0 ",
            "crf": "20",
        },
        "1080p.hevc": {
            "codec": "hevc",
            "ext": "265",
            "dr": "sdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "maxrate": "12000",
            "bufsize": "16000",
            "encode_speed": "slower",
            "encode_profile": "main10",
            "encode_level": "4.1",
            "encode_extra_settings": " --bframes 8 --qg-size 32 --no-rc-grain --psy-rd 0 ",
            "crf": "18",
        },
        "480p.hevc": {
            "codec": "hevc",
            "ext": "265",
            "dr": "sdr",
            "codded_width": "854",
            "codded_height": "480",
            "maxrate": "3000",
            "bufsize": "4000",
            "encode_speed": "slower",
            "encode_profile": "main10",
            "encode_level": "3.1",
            "encode_extra_settings": " --bframes 8 --qg-size 32 --no-rc-grain --psy-rd 0 ",
            "crf": "16",
        },

        "2160p.hevc.hdr": {
            "codec": "hevc",
            "ext": "265",
            "dr": "hdr",
            "codded_width": "3840",
            "codded_height": "2160",
            "maxrate": "30000",
            "bufsize": "40000",
            "encode_speed": "slower",
            "encode_profile": "main10",
            "encode_level": "5.1",
            "encode_extra_settings": " --bframes 8 --qg-size 32 --no-rc-grain --psy-rd 0 ",
            "crf": "17",
        },
        "1080p.hevc.hdr": {
            "codec": "hevc",
            "ext": "265",
            "dr": "hdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "maxrate": "12000",
            "bufsize": "16000",
            "encode_speed": "slower",
            "encode_profile": "main10",
            "encode_level": "4.1",
            "encode_extra_settings": " --bframes 8 --qg-size 32 --no-rc-grain --psy-rd 0 ",
            "crf": "15",
        },

        "1080p.avc": {
            "codec": "avc",
            "ext": "264",
            "dr": "sdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "maxrate": "12000",
            "bufsize": "16000",
            "encode_speed": "veryslow",
            "encode_profile": "main",
            "encode_level": "4.1",
            "encode_extra_settings": " --bframes 8 --psy-rd 0 ",
            "crf": "18",
        },
        "480p.avc": {
            "codec": "avc",
            "ext": "264",
            "dr": "sdr",
            "codded_width": "854",
            "codded_height": "480",
            "maxrate": "3000",
            "bufsize": "4000",
            "encode_speed": "veryslow",
            "encode_profile": "main",
            "encode_level": "3.1",
            "encode_extra_settings": " --bframes 8 --psy-rd 0 ",
            "crf": "16",
        }
    },
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
