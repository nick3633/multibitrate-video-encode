# multibitrate-video-encode
Encode video to h264 and h265.

## Input
Recommend resolution:
 - 1920 x 1080 (Full HD)
 - 3840 x 2160 (Ultra HD)
 - 4096 x 2160 (DCI 4K)

FPS should be less than or equal to 30.

Crop value can be set to the input video.

The container of the input video should be Quicktime (.mov).

## metadata.json Examples
### SDR
``````
[
	{
		"role": "video",
		"path": "ED_HD_PRORES_422HQ.mov",
		"crop": {
			"top": 0,
			"bottom": 0,
			"left": 0,
			"right": 0
		}
	}
]
``````
### HDR 10
``````
[
	{
		"role": "video",
		"path": "Cosmos_Laundromat_HD_SDR_ProRes_422HQ.mov",
		"crop": {
			"top": 138,
			"bottom": 138,
			"left": 0,
			"right": 0
		}
	},
	{
		"role": "video_hdr",
		"path": "Cosmos_Laundromat_HD_HDR_ProRes_4444HQ.mov",
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
``````
### Dolby Vision HDR
``````
[
	{
		"role": "video",
		"path": "Cosmos_Laundromat_HD_SDR_ProRes_422HQ.mov",
		"crop": {
			"top": 138,
			"bottom": 138,
			"left": 0,
			"right": 0
		}
	},
	{
		"role": "video_hdr",
		"path": "Cosmos_Laundromat_HD_HDR_ProRes_4444HQ.mov",
		"crop": {
			"top": 138,
			"bottom": 138,
			"left": 0,
			"right": 0
		},
		"hdr": {
			"format": "dolby_vision",
			"dolby_vision": {
				"metadata": "Cosmos_Laundromat_Mapping.xml"
			}
		}
	}
]
``````
Dolby Vision metadata example: http://download.opencontent.netflix.com.s3.amazonaws.com/TechblogAssets/CosmosLaundromat/cosmos_laundromat_vdm_hdr_p3d65_pq_20160525_01_2048x858/vdm/hdr/p3d65_pq/20160525_01/metadata/cosmos_laundromat_vdm_hdr_p3d65_pq_20160525_01_2048x858_dovi_4000nit_metadata.xml\
Dolby Vision HDR encode is **_not_** supported

## Command line tools required
- python
- ffmpeg
- x264
- x265
- mediainfo

## Others
HDR10 video encoding may be added in the future
