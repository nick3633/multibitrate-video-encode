import subprocess
import json
import string
import random
import os
import time
import shutil


import encode_settings

ladder = encode_settings.encode_settings['audio_ladder']


def encode(quality, audio_info, reuse_audio_info):
    codec = ladder[quality]['codec']
    channel = ladder[quality]['channel']
    codec_settings = ladder[quality]['codec_settings']

    audio_path = audio_info['audio_path']
    if quality == 'atmos.eac3':
        audio_track = 'not_applicable'
    else:
        audio_track = audio_info['audio_tracks'][channel]['track']

    in_bucket_name = reuse_audio_info['in_bucket_name']
    out_bucket_name = reuse_audio_info['out_bucket_name']
    org_tmp_audio_file = reuse_audio_info['tmp_audio_file']

    if quality == 'atmos.eac3':
        tmp_audio_file = 'tmp.' + channel + '.wav'
    else:
        tmp_audio_file = 'tmp.' + channel + '.mov'
    output_audio_file_name = channel + '.' + codec
    output_audio_file_ext = codec
    output_audio_file = output_audio_file_name + '.' + output_audio_file_ext
    print(output_audio_file)
    if os.path.exists(output_audio_file):
        return {
            'in_bucket_name': in_bucket_name,
            'out_bucket_name': out_bucket_name,
            'tmp_audio_file': org_tmp_audio_file
        }

    if codec == 'eac3' and channel != 'object_based':
        codec_settings['Eac3Settings']['Dialnorm'] = round(audio_info['audio_loudness'][audio_track] * -1)
    elif codec == 'ac3':
        codec_settings['Ac3Settings']['Dialnorm'] = round(audio_info['audio_loudness'][audio_track] * -1)

    # create input file
    if tmp_audio_file != org_tmp_audio_file:
        if not os.path.exists(tmp_audio_file):
            if org_tmp_audio_file and os.path.exists(org_tmp_audio_file):
                os.remove(org_tmp_audio_file)
            if quality == 'atmos.eac3':
                shutil.copyfile(audio_path, tmp_audio_file)
            else:
                cmd = [
                    'ffmpeg -loglevel warning -i "' + audio_path + '"' +
                    ' -c:a copy -map 0:' + audio_track + ' -n "' + tmp_audio_file + '"'
                ]
                for item in cmd:
                    print(item)
                    subprocess.call(item, shell=True)

    # create input and output bucket
    while True:
        if in_bucket_name:
            break
        try:
            in_bucket_name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(63))
            cmd = 'aws s3api create-bucket --acl private --bucket "' + in_bucket_name + '"'
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            location = json.loads(result)['Location']
            break
        except subprocess.CalledProcessError or json.JSONDecodeError or KeyError:
            ...
    while True:
        if out_bucket_name:
            break
        try:
            out_bucket_name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(63))
            cmd = 'aws s3api create-bucket --acl private --bucket "' + out_bucket_name + '"'
            result = subprocess.check_output(cmd, shell=True).decode('utf-8')
            location = json.loads(result)['Location']
            break
        except subprocess.CalledProcessError or json.JSONDecodeError or KeyError:
            ...

    # upload input file to the bucket
    cmd = 'aws s3 sync "." "s3://' + in_bucket_name + '/" --exclude "*" --include "' + tmp_audio_file + '"'
    subprocess.call(cmd, shell=True)

    # submit job
    cmd = 'aws iam get-role --role-name MediaConvert_Default_Role'
    result = subprocess.check_output(cmd, shell=True).decode('utf-8')
    role = json.loads(result)['Role']['Arn']

    cmd = 'aws mediaconvert describe-endpoints'
    result = subprocess.check_output(cmd, shell=True).decode('utf-8')
    endpoint = json.loads(result)['Endpoints'][0]['Url']

    job = {
        "Inputs": [
            {
                "TimecodeSource": "ZEROBASED",
                "VideoSelector": {},
                "AudioSelectors": {
                    "Audio Selector 1": {
                        "DefaultSelection": "DEFAULT"
                    }
                },
                "FileInput": 's3://' + in_bucket_name + '/' + tmp_audio_file
                # "FileInput": 's3://test/test.mp4'
            }
        ],
        "OutputGroups": [
            {
                "Name": "File Group",
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": 's3://' + out_bucket_name + '/' + output_audio_file_name
                    }
                },
                "Outputs": [
                    {
                        "AudioDescriptions": [
                            {
                                "CodecSettings": codec_settings,
                                "AudioSourceName": "Audio Selector 1"
                            }
                        ],
                        "ContainerSettings": {
                            "Container": "RAW"
                        },
                        "Extension": output_audio_file_ext
                    }
                ],
                "CustomName": output_audio_file_name
            }
        ],
        "TimecodeConfig": {
            "Source": "ZEROBASED"
        }
    }
    cmd = (
            'aws mediaconvert create-job --role "' + role + '" --endpoint-url "' + endpoint + '"' +
            ' --settings "' + json.dumps(job).replace('"', '\\"') + '" --status-update-interval SECONDS_20'
    )
    result = subprocess.check_output(cmd, shell=True).decode('utf-8')
    job_id = json.loads(result)['Job']['Id']

    # get job status
    while True:
        time.sleep(10)
        cmd = (
                'aws mediaconvert list-jobs --query "Jobs[?Id==\'' + job_id + '\'].Status"' +
                ' --endpoint-url "' + endpoint + '"'
        )
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')
        status = json.loads(result)[0]
        if status == 'COMPLETE':
            break

    # download encoded media
    cmd = 'aws s3 sync "s3://' + out_bucket_name + '/" "."'
    subprocess.call(cmd, shell=True)

    return {
        'in_bucket_name': in_bucket_name,
        'out_bucket_name': out_bucket_name,
        'tmp_audio_file': tmp_audio_file
    }
