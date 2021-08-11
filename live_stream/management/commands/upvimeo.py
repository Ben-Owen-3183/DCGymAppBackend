from django.core.management.base import BaseCommand, CommandError
import logging
import gocardless_pro
import stripe
from django.conf import settings
import vimeo
import json
from live_stream.models import VimeoVideos
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta

# cronjob command
# python3 manage.py upvimeo >> live_stream/management/commands/logs.txt

v = vimeo.VimeoClient(
    settings.VIMEO_KEYS['token'],
    settings.VIMEO_KEYS['key'],
    settings.VIMEO_KEYS['secret']
)
prompt = '[' + str(datetime.now(tz=timezone.utc)) + '] '
all_videos = VimeoVideos.objects.all()


class Command(BaseCommand):

    def fetch_and_store_videos(self):
        response = v.get('https://api.vimeo.com/me/videos')
        decoded_response = response.json()
        current_datetime = datetime.now(tz=timezone.utc)
        videos_to_create = []

        with transaction.atomic():
            for video in decoded_response['data']:
                try:
                    video_id = video['uri'].split('/')[2]
                    stored_video = self.video_exists(video_id)
                    if stored_video == None:
                        type = ''
                        parent_folder = ''
                        try:
                            parent_folder = video['parent_folder']['name']
                        except Exception as e:
                            raise Exception('no parent folder')
                        if parent_folder == '_APP_FEED_POSTS':
                            type = 'Feed'
                        elif parent_folder == '_APP_SAVED_STREAMS':
                            type = 'OldStream'
                        else:
                            raise Exception('parent folder ignored')
                        num_of_files = len(video['files'])
                        videos_to_create.append(VimeoVideos(
                            type=type,
                            vimeo_id=video_id,
                            name=video['name'],
                            video_url=video['link'],
                            thumbnail_link=self.get_thumbnail_link(video['pictures']['sizes']),
                            last_updated=current_datetime,
                            upload_date=video['release_time']
                        ))
                    else:
                        stored_video.last_updated(current_datetime)
                except Exception as e:
                    pass
                    # logging.exception('vimeo')
        VimeoVideos.objects.bulk_create(videos_to_create)
        all_videos.update()
        current_datetime = current_datetime - timedelta(minutes=1)
        current_datetime.replace(day=1)
        response = VimeoVideos.objects.filter(last_updated__range=['1066-10-14T13:47:23Z', current_datetime]).delete()

    def video_exists(self, id):
        for video in all_videos:
            if video.vimeo_id == id:
                return video
        return None


    def get_thumbnail_link(self, data):
        current_link = data[0]['link_with_play_button']
        for files in data:
            if files['width'] == 1920:
                return files['link_with_play_button']
            else:
                current_link = files['link_with_play_button']
        return current_link

    def generic(self):
        response = v.get('https://api.vimeo.com/me/videos')
        data = response.json()

        index =  0
        print_keys = True

        print("\n--------------------------------------------------------")
        print("  video title: " + str(data['data'][index]['parent_folder']['name'])  + "/" + str(data['data'][index]['name']))
        print("--------------------------------------------------------\n")

        print("number of videos: " + str(len(data['data'])))

        print("files: " + str(len(data['data'][index]['files'])))
        print("uri: " + str(data['data'][index]['uri']))
        print("is_playable: " + str(data['data'][index]['is_playable']))
        print("type: " + str(data['data'][index]['type']))
        print("resource_key: " + str(data['data'][index]['resource_key']))
        print("transcode: " + str(data['data'][index]['transcode']))

        # print("link: " + str(data['data'][index]['link']))
        # print("picture: " + str(data['data'][index]['pictures']))
        print("upload: " + str(data['data'][index]['upload']))
        print("status: " + str(data['data'][index]['status']))
        print("parent_folder: " + str(data['data'][index]['parent_folder']['name']))
        # print("manage_link: " + str(data['data'][index]['manage_link']))

        # metadata.connections.pictures
        print(str(data['data'][index]['metadata']['connections']['pictures']))

        print("")
        if print_keys:
            for key in data['data'][index]['metadata'].keys():
                print(key)

        # vimeo.com/videos/576767845
        response = v.get('/videos/576767845')
        data = response.json()

        print(str(data['pictures']['sizes'][5]['link_with_play_button']))


    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS(prompt + 'starting task'))
            self.fetch_and_store_videos()
            # self.generic()
            self.stdout.write(self.style.SUCCESS(prompt + 'task finished correctly'))
        except Exception as e:
            logging.exception(e)
            self.stdout.write(prompt + 'Error: ' + str(e))






#