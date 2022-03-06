encode_settings = {
    "ladder": {
        "2160p.hevc": {
            "codec": "hevc",
            "dr": "sdr",
            "codded_width": "3840",
            "codded_height": "2160",
            "maxrate": "100000",
            "bufsize": "75000",
            "encode_profile": "main10",
            "encode_level": "5.1",
            "crf": "19",
        },
        "2160p.hevc.hdr": {
            "codec": "hevc",
            "dr": "hdr",
            "codded_width": "3840",
            "codded_height": "2160",
            "maxrate": "100000",
            "bufsize": "75000",
            "encode_profile": "main10",
            "encode_level": "5.1",
            "crf": "16",
        },

        "1080p.avc": {
            "codec": "avc",
            "dr": "sdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "maxrate": "40000",
            "bufsize": "30000",
            "encode_profile": "high",
            "encode_level": "4.1",
            "crf": "17",
        },
        "1080p.hevc": {
            "codec": "hevc",
            "dr": "sdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "maxrate": "40000",
            "bufsize": "30000",
            "encode_profile": "main10",
            "encode_level": "4.1",
            "crf": "17",
        },
        "1080p.hevc.hdr": {
            "codec": "hevc",
            "dr": "hdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "maxrate": "40000",
            "bufsize": "30000",
            "encode_profile": "main10",
            "encode_level": "4.1",
            "crf": "14",
        },

        "480p.avc": {
            "codec": "avc",
            "dr": "sdr",
            "codded_width": "854",
            "codded_height": "480",
            "maxrate": "10000",
            "bufsize": "7500",
            "encode_profile": "main",
            "encode_level": "3.1",
            "crf": "15",
        },
        "480p.hevc": {
            "codec": "hevc",
            "dr": "sdr",
            "codded_width": "854",
            "codded_height": "480",
            "maxrate": "10000",
            "bufsize": "7500",
            "encode_profile": "main10",
            "encode_level": "3.1",
            "crf": "15",
        }
    },
    "audio_ladder": {
        "atmos.eac3": {
            "codec": "eac3",
            "channel": "object_based",
            'codec_settings': {
                "Codec": "EAC3_ATMOS",
                "Eac3AtmosSettings": {
                    "Bitrate": 768000,
                    "DynamicRangeControl": "INITIALIZE_FROM_SOURCE",
                    "SurroundExMode": "NOT_INDICATED",
                    "DownmixControl": "INITIALIZE_FROM_SOURCE",
                    "MeteringMode": "ITU_BS_1770_4",
                    "DialogueIntelligence": "ENABLED",
                    "SpeechThreshold": 10
                }
            }
        },

        "5_1.eac3": {
            "codec": "eac3",
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
