# multibitrate-video-encode (automator)
This programme can automatic generate and run command-line programme to simplify the process of video and audio encoding.\
This programme will split the video to multiple parts when encoding and then recombine the encoded video.

### This programme can:
Encode video to H264 and H265.\
Output resolution includes 2160p, 1080p and 480p.\
Supports SDR and HDR10 video

Encode Audio to Dolby Digital Plus, Dolby Digital and AAC in stereo and 5.1 surround.\
Encode Audio to Dolby Atmos.

Audio encoding are done by 3rd party cloud service provider (aws mediaconvert)

## Video Input
Recommend resolution:
 - 1920 x 1080 (Full HD)
 - 3840 x 2160 (Ultra HD)
 - 4096 x 2160 (DCI 4K)

FPS should be less than or equal to 30.\
Crop value can be set to the input video.\
The container of the input video should be Quicktime (.mov).\
The number of frames, FPS, resolution must be the same for both HDR and SDR version of the input video.\
Input files should be placed in the same directory with metadata.json.

## Audio Input
5.1 surround (L R C LFE Ls Rs) and stereo (L R) embedded in main video file or as a seperate file.\
Audio duration and video duration should be the same.

Dolby Atmos master file (BWF ADM) in .wav extension.\
It should be synced and have the same duration with the primary audio.

## metadata.json Examples
### SDR without embedded 5.1 + 2.0 audio
``````
{
    "title": "Content Title",
    "language": "en",
    "asset": [
    {
    "role": "video",
        "language": "en",
        "path": "ED_HD_PRORES_422HQ.mov",
        "crop": {
            "top": 0,
            "bottom": 0,
            "left": 0,
            "right": 0
        }
    },
    {
        "role": "audio",
        "language": "en",
        "path": "ED_Audio.mov",
        "primary_audio": true,
        "loudness": {
            "0": -27,
            "1": -27
        }
    }
]
}
``````
### HDR 10 with embedded 2.0 audio
``````
{
    "title": "Content Title",
    "language": "en",
    "asset": [
    {
        "role": "video",
        "language": "en",
        "path": "Cosmos_Laundromat_HD_SDR_ProRes_422HQ.mov",
        "crop": {
            "top": 138,
            "bottom": 138,
            "left": 0,
            "right": 0
        },
        "loudness": {
            "0": -27
        }
    },
    {
        "role": "video_hdr",
        "language": "en",
        "path": "Cosmos_Laundromat_HD_HDR_ProRes_4444.mov",
        "crop": {
            "top": 138,
            "bottom": 138,
            "left": 0,
            "right": 0
        },
        "hdr": {
            "format": "hdr10",
            "hdr10": {
                "mastering_display": {
                    "red_x": 0.68,
                    "red_y": 0.32,
                    "green_x": 0.265,
                    "green_y": 0.69,
                    "blue_x": 0.15,
                    "blue_y": 0.06,
                    "white_point_x": 0.3127,
                    "white_point_y": 0.329,
                    "luminance_min": 0.005,
                    "luminance_max": 4000
                },
                "content_lightlevel": {
                    "max": 0,
                    "max_frame_avg": 0
                }
            }
        }
    }
]
}
``````
### Dolby Vision HDR with embedded audio and alternative audio file 5.1 + 2.0 provided as primary audio + Dolby Atmos
```
{
    "title": "Content Title",
    "language": "en",
    "asset": [
    {
        "role": "video",
        "language": "en",
        "path": "SolLevante_3840x2160_SDR_Prores_422HQ.mov",
        "crop": {
            "top": 0,
            "bottom": 0,
            "left": 0,
            "right": 0
        },
        "ignore_audio": true
    },
    {
        "role": "video_hdr",
        "language": "en",
        "path": "SolLevante_3840x2160_HDR_Prores_4444.mov",
        "crop": {
            "top": 0,
            "bottom": 0,
            "left": 0,
            "right": 0
        },
        "hdr": {
            "format": "dolby_vision",
            "dolby_vision": {
                "metadata": "SolLevante_DolbyVision_Metadata.xml"
            }
        }
    },
    {
        "role": "audio",
        "language": "en",
        "path": "SolLevante_Audio.mov",
        "primary_audio": true,
        "loudness": {
            "0": -27
            "1": -27
        }
    },
    {
        "role": "audio_object_based",
        "language": "en",
        "path": "SolLevante_DolbyAtmos.wav"
    }
]
}
```

Dolby Vision metadata example: http://download.opencontent.netflix.com.s3.amazonaws.com/TechblogAssets/CosmosLaundromat/cosmos_laundromat_vdm_hdr_p3d65_pq_20160525_01_2048x858/vdm/hdr/p3d65_pq/20160525_01/metadata/cosmos_laundromat_vdm_hdr_p3d65_pq_20160525_01_2048x858_dovi_4000nit_metadata.xml \
This program can't encode Dolby Vision
## Command line tools required
- python
- ffmpeg
- ffprobe
- x264
- x265
- mediainfo
- mp4box
- aws cli2

## run the program
``````
sys.path.insert(1, '{directory of this repository}')
import main
main.main('{directory of the metadata.json}')
``````
