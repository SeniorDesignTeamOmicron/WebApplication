from datetime import datetime
from django.db.models import Count, Max, Min
from math import floor
from logisteps.models import Step, LogistepsUser

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

def avgStepsPerHour(queryset, date):
    steps = queryset.count()
    now = datetime.now()

    if date == now.date():
        hours_elapsed = now - now.replace(hour=0, minute=0, second=0, microsecond=0).total_hours()
        steps_per_hour = steps / hours_elapsed
    else:
        steps_per_hour = steps / 24
    
    return steps_per_hour

def getStepsOnDate(user, date):
    """
    Returns set of steps taken by a user on a particular date. If date is blank,
    steps for the current date are returned.
    """
    queryset = Step.objects.all()

    if date is None:
        query_date = datetime.today()
    elif isinstance(date, str):
        query_date = datetime.strptime(date, '%m-%d-%Y')
    else:
        query_date = date

    logistepsUser = LogistepsUser.objects.get(user_id=user.id)

    if logistepsUser is not None:
        queryset = queryset.filter(user=logistepsUser.id,
                                    datetime__year=query_date.year,
                                    datetime__month=query_date.month,
                                    datetime__day=query_date.day)
    return queryset

def getDateSummary(user, date):
    """
    Returns a dictionary object summarzing a User's step statistics for a 
    given day
    """
    queryset = getStepsOnDate(user, date)
    logistepsUser = LogistepsUser.objects.get(user_id=user.id)

    steps = queryset.count()
    goal = logistepsUser.step_goal
    percent_complete = float(steps)/goal * 100

    most_active_hour = getMostActiveHour(queryset)
    least_active_hour = getLeastActiveHour(queryset)
    inactive_time = getInactiveTime(queryset)
    steps_per_hour = avgStepsPerHour(queryset, date)

    # do statistics here, e.g.
    stats = {
        'steps': steps,
        'goal': goal,
        'percent': percent_complete,
        'least_active': {
            'hour': least_active_hour.get('datetime__hour'),
            'steps': least_active_hour.get('id__count')
        },
        'most_active': {
            'hour': most_active_hour.get('datetime__hour'),
            'steps': most_active_hour.get('id__count')
        },
        'inactive_time': inactive_time,
        'steps_per_hour': steps_per_hour
    }

    # not using a serializer here since it is already a 
    # form of serialization
    return stats
