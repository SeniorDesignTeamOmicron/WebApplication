from datetime import datetime, date, timedelta
from django.db.models import Count, Max, Min, Avg
from django.db.models.functions import ExtractWeekDay, ExtractMonth
from math import floor
from logisteps.models import Step, LogistepsUser, SensorReading

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

def getStepCount(user, date):
    """
    Returns the number of steps taken in a given day.
    """
    logistepsUser = LogistepsUser.objects.get(user_id=user.id)
    return getStepsOnDate(user, date).count()

def getStepCounts(user, start, end):
    """
    Returns a dictionary object containing step counts for every
    day in the date range.
    """

    step_counts = {
        'range': {
            'start': start.strftime("%m-%d-%Y"),
            'end': end.strftime("%m-%d-%Y")
        }
    }

    counts = {}
    day = timedelta(days=1)
    dateIndex = start

    while dateIndex <= end:
        counts[dateIndex.strftime("%m-%d-%Y")] = getStepCount(user, dateIndex)
        dateIndex += day
    
    step_counts['count'] = counts

    return step_counts

def getStepBreakdown(user, groupyby):
    MINUTES_IN_YEAR = 60 * 24 * 365
    logistepsUser = LogistepsUser.objects.get(user_id=user.id)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    steps = Step.objects.all().filter(user=logistepsUser.id, datetime__range=[start_date, end_date])

    active_minutes = steps.values('datetime','datetime__year','datetime__month', 'datetime__day', 'datetime__hour', 'datetime__minute') \
        .annotate(Count('datetime__year'),Count('datetime__month'), Count('datetime__day'), Count('datetime__hour'), Count('datetime__minute'))
    
    if groupyby == 'weekly':
        MINUTES_IN_WEEKDAY = MINUTES_IN_YEAR / 7
        active_minutes = active_minutes.annotate(weekday=ExtractWeekDay('datetime')) \
            .values('weekday') 

        lst = [0] * 7
        for minute in active_minutes:
            lst[minute.get('weekday')-1] += 1

        steps = steps.annotate(weekday=ExtractWeekDay('datetime')) \
            .values('weekday') \
            .annotate(count=Count('id')) \
            .values('weekday', 'count')

        for obj in steps:
            weekday = obj.get('weekday')

            active_min = lst[weekday - 1]
            inactive_min = MINUTES_IN_WEEKDAY - active_min

            obj['inactive_minutes'] = inactive_min
            obj['active_minutes'] = active_min
    elif groupyby == 'monthly':
        MINUTES_IN_MONTH = MINUTES_IN_YEAR / 12
        active_minutes = active_minutes.annotate(month=ExtractMonth('datetime')) \
            .values('month')
        
        lst = [0] * 12
        for minute in active_minutes:
            lst[minute.get('month')-1] += 1
        
        steps = steps.annotate(month=ExtractMonth('datetime')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .values('month', 'count')
        
        for obj in steps:
            month = obj.get('month')

            active_min = lst[month - 1]
            inactive_min = MINUTES_IN_MONTH - active_min

            obj['inactive_minutes'] = inactive_min
            obj['active_minutes'] = active_min
    
    return steps

def getAvgPressureBySensor(steps, shoe, date_range):
    steps = steps.filter(datetime__range=date_range)    
    return SensorReading.objects.filter(id__in=steps.values_list('sensor_reading_id', flat=True), shoe_id=shoe) \
        .values('location') \
        .annotate(avg_pressure=Avg('pressure'))

def getPressureSnapshot(user, date):
    logisetpsUser = LogistepsUser.objects.get(user_id=user.id)
    left_shoe = logisetpsUser.left_shoe_id
    right_shoe = logisetpsUser.right_shoe_id

    steps = Step.objects.all().filter(user_id=logisetpsUser.id, datetime__range=[date - timedelta(days=30), date])

    return {
        'query_date': date.strftime("%m-%d-%Y"),
        'pressure': {
            'past_day': {
                'left_shoe': getAvgPressureBySensor(steps, left_shoe, [date - timedelta(days=1), date]),
                'right_shoe': getAvgPressureBySensor(steps, right_shoe, [date - timedelta(days=1), date])
            },
            'past_week': {
                'left_shoe': getAvgPressureBySensor(steps, left_shoe, [date - timedelta(days=7), date]),
                'right_shoe': getAvgPressureBySensor(steps, right_shoe, [date - timedelta(days=7), date])
            },
            'past_month': {
                'left_shoe': getAvgPressureBySensor(steps, left_shoe, [date - timedelta(days=30), date]),
                'right_shoe': getAvgPressureBySensor(steps, right_shoe, [date - timedelta(days=30), date])
            }
        }
    }
