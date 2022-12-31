encode_settings = '''
{
  "video_encode_list": {
    "2160p.hevc": {
      "codec": "hevc",
      "dr": "sdr",
      "codded_width": "3840",
      "codded_height": "2160",
      "maxrate": "24000",
      "max_avg_rate": "24000",
      "bufsize": "32000",
      "encode_speed": "slow",
      "encode_profile": "main",
      "encode_extra_settings": "--no-open-gop --no-sao --aq-mode 3 --psy-rd 1 --rc-lookahead 60 --bframes 8 --ref 5",
      "crf": "22"
    },
    "1080p.hevc": {
      "codec": "hevc",
      "dr": "sdr",
      "codded_width": "1920",
      "codded_height": "1080",
      "maxrate": "9000",
      "max_avg_rate": "9000",
      "bufsize": "12000",
      "encode_speed": "slow",
      "encode_profile": "main",
      "encode_extra_settings": "--no-open-gop --no-sao --aq-mode 3 --psy-rd 1 --rc-lookahead 60 --bframes 8 --ref 5",
      "crf": "20.5"
    },
    "2160p.hevc.hdr": {
      "codec": "hevc",
      "dr": "hdr",
      "codded_width": "3840",
      "codded_height": "2160",
      "maxrate": "30000",
      "max_avg_rate": "30000",
      "bufsize": "40000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-open-gop --no-sao --aq-mode 2 --psy-rd 1 --rc-lookahead 60 --bframes 8 --ref 5",
      "crf": "16"
    },
    "1080p.hevc.hdr": {
      "codec": "hevc",
      "dr": "hdr",
      "codded_width": "1920",
      "codded_height": "1080",
      "maxrate": "11250",
      "max_avg_rate": "11250",
      "bufsize": "15000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-open-gop --no-sao --aq-mode 2 --psy-rd 1 --rc-lookahead 60 --bframes 8 --ref 5",
      "crf": "14.5"
    },
    "1080p.avc": {
      "codec": "avc",
      "dr": "sdr",
      "codded_width": "1920",
      "codded_height": "1080",
      "maxrate": "12000",
      "max_avg_rate": "12000",
      "bufsize": "16000",
      "encode_speed": "slower",
      "encode_profile": "high",
      "encode_extra_settings": "--no-fast-pskip --no-dct-decimate --aq-mode 3 --rc-lookahead 60 --bframes 8 --ref 5",
      "crf": "19"
    },
    "480p.avc": {
      "codec": "avc",
      "dr": "sdr",
      "codded_width": "854",
      "codded_height": "480",
      "maxrate": "3750",
      "max_avg_rate": "3750",
      "bufsize": "5000",
      "encode_speed": "slower",
      "encode_profile": "main",
      "encode_extra_settings": "--no-fast-pskip --no-dct-decimate --aq-mode 3 --rc-lookahead 60 --bframes 8 --ref 5",
      "crf": "15.5"
    }
  },
  "video_other_settings": {
    "chunked_encoding": false,
    "sdr_highest_res_only": false,
    "hdr_highest_res_only": true,
    "replace_sdr_with_hdr": false,
    "hls_compatible": true,
    "hls_compatible_settings": {
      "keyint": [4, "s"],
      "dynamic_keyint": true
    },
    "two_pass_encoding": true
  }
}
'''