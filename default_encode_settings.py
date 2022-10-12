encode_settings = '''
{
  "video_encode_list": {
    "2160p.hevc": {
      "codec": "hevc",
      "dr": "sdr",
      "codded_width": "3840",
      "codded_height": "2160",
      "maxrate": "30000",
      "bufsize": "40000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-sao --aq-mode 1",
      "crf": "20.3"
    },
    "1080p.hevc": {
      "codec": "hevc",
      "dr": "sdr",
      "codded_width": "1920",
      "codded_height": "1080",
      "maxrate": "12000",
      "bufsize": "16000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-sao --aq-mode 1",
      "crf": "18"
    },
    "480p.hevc": {
      "codec": "hevc",
      "dr": "sdr",
      "codded_width": "854",
      "codded_height": "480",
      "maxrate": "3000",
      "bufsize": "4000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-sao --aq-mode 1",
      "crf": "16.4"
    },
    "2160p.hevc.hdr": {
      "codec": "hevc",
      "dr": "hdr",
      "codded_width": "3840",
      "codded_height": "2160",
      "maxrate": "30000",
      "bufsize": "40000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-sao --aq-mode 1",
      "crf": "17.3"
    },
    "1080p.hevc.hdr": {
      "codec": "hevc",
      "dr": "hdr",
      "codded_width": "1920",
      "codded_height": "1080",
      "maxrate": "12000",
      "bufsize": "16000",
      "encode_speed": "slow",
      "encode_profile": "main10",
      "encode_extra_settings": "--no-sao --aq-mode 1",
      "crf": "15"
    },
    "1080p.avc": {
      "codec": "avc",
      "dr": "sdr",
      "codded_width": "1920",
      "codded_height": "1080",
      "maxrate": "12000",
      "bufsize": "16000",
      "encode_speed": "medium",
      "encode_profile": "high",
      "encode_extra_settings": "",
      "crf": "18"
    },
    "480p.avc": {
      "codec": "avc",
      "dr": "sdr",
      "codded_width": "854",
      "codded_height": "480",
      "maxrate": "3000",
      "bufsize": "4000",
      "encode_speed": "medium",
      "encode_profile": "main",
      "encode_extra_settings": "",
      "crf": "16.4"
    }
  },
  "video_other_settings": {
    "chunked_encoding": false,
    "sdr_highest_res_only": false,
    "hdr_highest_res_only": true,
    "replace_sdr_with_hdr": true,
    "hls_compatible": false,
    "hls_compatible_settings": {
      "keyint_second": 6
    }
  }
}
'''