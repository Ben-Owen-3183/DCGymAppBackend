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
        current_datetime = datetime.now(tz=timezone.utc)
        decoded_video_data = []
        current_page = 1

        response = self.fetch_videos(current_page)
        decoded_response = response.json()
        decoded_video_data = decoded_video_data + decoded_response['data']

        while decoded_response['paging']['next'] != None:
            current_page += 1
            response = self.fetch_videos(current_page)
            decoded_response = response.json()
            decoded_video_data = decoded_video_data + decoded_response['data']


        self.process_and_store_videos(
            videos=decoded_video_data, 
            current_datetime=current_datetime
        )

        
    def fetch_videos(self, current_page):
        response = v.get('https://api.vimeo.com/me/videos', params={
            'page': current_page,
            'per_page': 25
        })
        return response


    def process_and_store_videos(self, videos, current_datetime):
        videos_to_create = []

        with transaction.atomic():
            for video in videos:
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
                            upload_date=current_datetime
                        ))
                    else:
                        stored_video.name = video['name']                    
                        stored_video.last_updated = current_datetime
                        stored_video.thumbnail_link = self.get_thumbnail_link(video['pictures']['sizes'])
                        stored_video.save()
                except Exception as e:
                    if settings.DEBUG == True:
                        logging.exception('vimeo')
                    
        self.set_videos_privacy(videos_to_create)
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


    def set_videos_privacy(self, videos):
        """
        Vimeo is broken and live stream created videos will not work as
        embeded players in mobile webviews if privacy is set to private link.
        This sets them to unlisted. Ignore the fact that disabled is used. 
        Vimeo api also seems to treat private as unlisted and unlisted as private.
        Api also confusing as it uses different words from the UI. 
        Change at your own risk. 
        """
        try:
            for video in videos:
                try:
                    response = v.patch('/videos/' + video.vimeo_id, data={'privacy': {'view': 'disable'}}) 
                except:
                    print(prompt + 'failed to set privacy for video ' + video.name)
        except:
            print(prompt + 'set_videos_privacy() failed')
            return


    def get_thumbnail_link(self, data):
        current_link = data[0]['link_with_play_button']
        for files in data:
            if files['width'] == 960:
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
