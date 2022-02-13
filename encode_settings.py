encode_settings = {
    "ladder": {
        "2160p.hevc": {
            "codec": "hevc",
            "dr": "sdr",
            "codded_width": "3840",
            "codded_height": "2160",
            "pass1_target_rate": 32000,
            "pass2_rate_fac": [21, 40],
            "encode_level": "5.0",
            "crf": "24",
        },
        "2160p.hevc.hdr": {
            "codec": "hevc",
            "dr": "hdr",
            "codded_width": "3840",
            "codded_height": "2160",
            "pass1_target_rate": [200000, 9],
            "pass2_rate_fac": [9, 10],
            "encode_level": "5.0",
            "crf": "21",
        },

        "1080p.avc": {
            "codec": "avc",
            "dr": "sdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "pass1_target_rate": 8000,
            "pass2_rate_fac": [39, 40],
            "encode_level": "4.0",
            "crf": "22",
        },
        "1080p.hevc": {
            "codec": "hevc",
            "dr": "sdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "pass1_target_rate": 8000,
            "pass2_rate_fac": [29, 40],
            "encode_level": "4.0",
            "crf": "22",
        },
        "1080p.hevc.hdr": {
            "codec": "hevc",
            "dr": "hdr",
            "codded_width": "1920",
            "codded_height": "1080",
            "pass1_target_rate": [50000, 9],
            "pass2_rate_fac": [63, 50],
            "encode_level": "4.0",
            "crf": "19",
        }
    }
}
