def to12HourTime(twentyFourHourTime):
        if twentyFourHourTime == 0:
            return '12 AM'
        elif twentyFourHourTime <= 12:
            return str(twentyFourHourTime) + ' AM'
        else:
            return str(twentyFourHourTime - 12) + ' PM'