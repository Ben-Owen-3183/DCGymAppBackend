from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from live_stream.models import VimeoVideos, VimeoLiveStreams
from django.core.paginator import Paginator
from datetime import datetime

def video_row_to_json(videos):
    json_videos = []
    for video in videos:
        json_videos.append({
            'id': video.vimeo_id,
            'name': video.name,
            'file': video.video_url,
            'thumbnail': video.thumbnail_link,
            'last_updated': video.last_updated,
            'upload_date': video.upload_date,
        })
    return json_videos


class GetLiveStream(APIView):
    def get(self, request):
        try:
            live_streams = VimeoLiveStreams.objects.all().order_by('time_from')
            stream_by_day = {
                'Monday': [],
                'Tuesday': [],
                'Wednesday': [],
                'Thursday': [],
                'Friday': [],
                'Saturday': [],
                'Sunday': [],
            }
            for stream in live_streams:
                time_from = datetime.strptime(str(stream.time_from), "%H:%M:%S")
                time_to = datetime.strptime(str(stream.time_to), "%H:%M:%S")
                time_from_str = time_from.strftime("%-I:%M%p")
                time_to_str = time_to.strftime("%-I:%M%p")

                stream_by_day[stream.day].append({
                    'name': stream.name,
                    'time': time_from_str + '-' + time_to_str,
                    'stream_url': stream.stream_url,
                    'chat_url': stream.chat_url,
                })
            return Response({'streams_by_day': stream_by_day})

        except Exception as e:
            logging.exception('Live Stream')
            return Response({'errors': 'request failed'})


class GetVideos(APIView):
    max_page_size = 30

    def post(self, request):
        try:
            page_length = request.data['page_length']
            page_number = request.data['page_number']
            if page_length > self.max_page_size:
                page_length = self.max_page_size
            pages = Paginator(VimeoVideos.objects.filter(type='OldStream').order_by('-upload_date'), page_length)
            if page_number > pages.num_pages:
                return Response({'videos': []})
            videos = pages.page(page_number)
            return Response({'videos': video_row_to_json(videos)})
        except Exception as e:
            logging.exception('GetVideos')
            return Response({'errors': 'request failed'})
