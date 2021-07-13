from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from timetable.models import TimeTable
import logging

class GetTimeTable(APIView):

    def day_to_json(self, day):
        day_data = []
        for row in day:
            day_data.append({
                'live': row.live,
                'name': row.day,
                'time_from': row.time_from,
                'time_to': row.time_to,
                'excercise': row.excercise,
                'instructor': row.instructor,
            })
        return day_data

    def timetable_to_json(self):

        monday = TimeTable.objects.filter(day='Monday').order_by('time_from')
        tuesday = TimeTable.objects.filter(day='Tuesday').order_by('time_from')
        wednesday = TimeTable.objects.filter(day='Wednesday').order_by('time_from')
        thursday = TimeTable.objects.filter(day='Thursday').order_by('time_from')
        friday = TimeTable.objects.filter(day='Friday').order_by('time_from')
        saturday = TimeTable.objects.filter(day='Saturday').order_by('time_from')
        sunday = TimeTable.objects.filter(day='Sunday').order_by('time_from')

        timetable_data = [
            {'classes': self.day_to_json(monday), 'name': 'monday'},
            {'classes': self.day_to_json(tuesday), 'name': 'tuesday'},
            {'classes': self.day_to_json(wednesday), 'name': 'wednesday'},
            {'classes': self.day_to_json(thursday), 'name': 'thursday'},
            {'classes': self.day_to_json(friday), 'name': 'friday'},
            {'classes': self.day_to_json(saturday), 'name': 'saturday'},
            {'classes': self.day_to_json(sunday), 'name': 'sunday'},
        ]
        return timetable_data

    def get(self, request):
        try:
            return Response({'timetable': self.timetable_to_json()})
        except Exception as e:
            logging.exception('TimeTable')
            return Response({'errors': 'request failed'})
