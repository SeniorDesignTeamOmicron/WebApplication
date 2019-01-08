from datetime import datetime
from django.db.models import Count, Max, Min
from math import floor

def getOrderStepsByHour(queryset):
    return queryset.values('datetime__hour').annotate(Count('id')).order_by('id__count')


def getMostActiveHour(queryset):
    """
        Finds the most active hour in a given queryset. This is
        determined by finding the timeslice with the most steps
    """
    return getOrderStepsByHour(queryset).last()

def getLeastActiveHour(queryset):
    """
        Finds the least active hour in a given queryset. This is
        determined by finding the timeslice with the least steps
    """
    return getOrderStepsByHour(queryset).first()

def getInactiveTime(queryset):
    """
        Determines the amount of inactive minutes by slicing the queryset
        by minutes. Each unique minute with a recorded step then counts as
        an active minute. Inactive minutes are subtracted by total time in day.
    """
    active_minutes = queryset.values('datetime__hour', 'datetime__minute').annotate(Count('datetime__hour'), Count('datetime__minute')).count()
    inactive_minutes = (60 * 24) - active_minutes
    
    hours = floor(inactive_minutes / 60)
    minutes = inactive_minutes % 60

    return {
        'hours': hours,
        'minutes': minutes
    }