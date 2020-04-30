"""
The bald datetime module supplies classes for manipulating dates and times in
 both simple and complex ways. While date and time arithmetic is supported, the
 focus of the implementation is on efficient attribute extraction for output
 formatting and manipulation.

The interface is based on Python's :mod:`datetime.datetime`. This has effects,
 including the naming of classes without capitalisation where they support
 the Python :mod:`datetime.datetime` interface.

Different Calendars are supported, but numerical conversions between calendars
 is not supported, this is not a safe operation to generalise, case specific
 knowledge and logic is required.

"""
import copy
import numpy as np
import numpy.ma
import re
import requests

from bald import units

# must be in context to know what 'CAL' means
# '^([0-9]{4})-([0-9]{2})-([0-9]{2})(CAL)([0-9]{2}):([0-9]{2}):([0-9]{2})'
dtstring_patterns = [re.compile('^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
                                '(T)([0-9]{2}):([0-9]{2}):([0-9]{2})'),
                     re.compile('^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
                                '( )([0-9]{2}):([0-9]{2}):([0-9]{2})'),
                     re.compile('^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})')]


def parse_datetime(instring, calendar):
    """
    Returns a `bald.datetime.datetime` from a given string and bald Calendar.

    """
    if not isinstance(calendar, Calendar):
        raise TypeError('calendar must be a bald.datetime.Calendar.')
    result = None
    for pattern in dtstring_patterns:
        match = pattern.match(instring)
        if match and len(match.groups()) == 7:
            result = datetime(int(match.group(1)), int(match.group(2)),
                              int(match.group(3)), int(match.group(5)),
                              int(match.group(6)), int(match.group(7)),
                              calendar=calendar, tsep=match.group(4))
        elif match and len(match.groups()) == 3:
            result = datetime(int(match.group(1)), int(match.group(2)),
                              int(match.group(3)), calendar=calendar)
    return result


class date(object):
    """
    An idealized naive date,  Attributes: year, month, and day.

    Objects of this type are not immutable.

    """
    def __init__(self, year, month, day, calendar=None):
        self.year = year
        self.day = day
        self.calendar = calendar
        if calendar is not None:
            if month in [mn[0:3] for mn in calendar.month_names]:
                for i, mon in enumerate([mn[0:3] for mn in
                                         calendar.month_names]):
                    if month == mon:
                        month = i + 1
        self.month = month

    def __str__(self):
        return '{0:0>4}-{1:0>2}-{2:0>2}'.format(self.year, self.month,
                                                self.day)

    def __repr__(self):
        return 'bald.datetime.date({}, {}, {})'.format(self.year,
                                                        self.month,
                                                        self.day)

    def __lt__(self, other):
        if not isinstance(other, date):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        yearlt = self.year < other.year
        yeare = self.year == other.year
        monthlt = self.month < other.month
        monthe = self.month == other.month
        daylt = self.day < other.day
        result = False
        if yearlt:
            result = True
        elif yeare:
            if monthlt:
                result = True
            elif monthe:
                if daylt:
                    result = True
        return result

    def __le__(self, other):
        if not isinstance(other, date):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        return self.__lt__(other) or self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, date):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        yeare = self.year == other.year
        monthe = self.month == other.month
        daye = self.day == other.day
        return yeare and monthe and daye

    def __ne__(self, other):
        if not isinstance(other, date):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        return not self == other

    def __gt__(self, other):
        if not isinstance(other, date):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        yeargt = self.year > other.year
        yeare = self.year == other.year
        monthgt = self.month > other.month
        monthe = self.month == other.month
        daygt = self.day > other.day
        result = False
        if yeargt:
            result = True
        elif yeare:
            if monthgt:
                result = True
            elif monthe:
                if daygt:
                    result = True
        return result

    def __ge__(self, other):
        if not isinstance(other, date):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        return self.__gt__(other) or self.__eq__(other)

    def __sub__(self, other):
        if isinstance(other, date):
            if not self.calendar == other.calendar:
                raise NotImplementedError('{} != {}'.format(self.calendar,
                                                            other.calendar))
            return CalendarDuration(self, other)
        elif isinstance(other, timedelta):
            if self.calendar is None:
                calendar = GregorianNoLeapSecond()
            else:
                calendar = self.calendar
            newyear = self.year
            newmonth = self.month
            newday = self.day
            if other.quantity == 'days':
                for day in range(other.value):
                    newday = newday - 1
                    days_in_month = calendar.month_day_map[newmonth - 1]
                    if (calendar.is_leap_year(newyear) and
                       newmonth == calendar.leap_year_date.month):
                        days_in_month -= 1
                    if newday > days_in_month:
                        newday = newday - days_in_month
                        newmonth -= 1
                        if newmonth > calendar.months_in_year:
                            yearstep = 1
                            if not calendar.is_valid_year(newyear + yearstep):
                                yearstep = 2
                                if not calendar.is_valid_year(newyear + yearstep):
                                    msg = ('There are two adjacent skip years in '
                                           'this calendar period: {}, {}.')
                                    msg = msg.format(newyear+1, newyear+2)
                                    raise ValueError(msg)
                            newyear -= yearstep
                            newmonth = newmonth - calendar.months_in_year

            return date(newyear, newmonth, newday, self.calendar)

        else:
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)

    def __add__(self, other):
        if not isinstance(other, timedelta):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if other.quantity in ['microseconds', 'seconds', 'minutes', 'hours']:
            raise ValueError('{} may not be added to a date'
                             '.'.format(other.quantity))

        if self.calendar is None:
            calendar = GregorianNoLeapSecond()
        else:
            calendar = self.calendar
        newyear = self.year
        newmonth = self.month
        newday = self.day

        if other.quantity == 'days':
            for day in range(other.value):
                newday = newday + 1
                days_in_month = calendar.month_day_map[newmonth - 1]
                if (calendar.is_leap_year(newyear) and
                   newmonth == calendar.leap_year_date.month):
                    days_in_month += 1
                if newday > days_in_month:
                    newday = newday - days_in_month
                    newmonth += 1
                    if newmonth > calendar.months_in_year:
                        yearstep = 1
                        if not calendar.is_valid_year(newyear + yearstep):
                            yearstep = 2
                            if not calendar.is_valid_year(newyear + yearstep):
                                msg = ('There are two adjacent skip years in this '
                                       'calendar period: {}, {}.')
                                msg = msg.format(newyear+1, newyear+2)
                                raise ValueError(msg)
                        newyear += yearstep
                        newmonth = newmonth - calendar.months_in_year
        elif other.quantity == 'months':
            for month in range(other.value):
                newmonth += 1
                if newmonth > calendar.months_in_year:
                    yearstep = 1
                    if not calendar.is_valid_year(newyear + yearstep):
                        yearstep = 2
                        if not calendar.is_valid_year(newyear + yearstep):
                            msg = ('There are two adjacent skip years in this '
                                   'calendar period: {}, {}.')
                            msg = msg.format(newyear+1, newyear+2)
                            raise ValueError(msg)
                    newyear += yearstep
                    newmonth = newmonth - calendar.months_in_year
                

        elif other.quantity == 'years':
            newyear = newyear + other.value

        return date(newyear, newmonth, newday, self.calendar)


class time(object):
    """
    An idealized instant in time, independent of any particular day.

    Attributes: hour, minute, second, microsecond, and tzinfo.

    Objects of this type are not immutable.

    """
    def __init__(self, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        """
        Create a time instance.

        Attrs:
            hour - int, default 0
            minute - int, default 0
            second - float/int, default 0
            microsecond - int, default 0
            tzinfo
        """
        self.hour = hour
        self.minute = minute
        self.second = second
        if isinstance(second, float):
            if microsecond != 0:
                raise ValueError('float seconds and microseconds cannot'
                                 ' both be specified')
            self.microsecond = None
        else:
            self.microsecond = microsecond
        self.tzinfo = tzinfo

    def __str__(self):

        ms = ''
        if self.microsecond and isinstance(self.second, int):
            ms = '.{0:0>6}'.format(self.microsecond)
        elif isinstance(self.second, float):
            ms = '.{0:0>6}'.format(int((self.second % 1) * 1e6))
        return '{0:0>2}:{1:0>2}:{2:0>2}{3}'.format(self.hour, self.minute,
                                                   int(self.second), ms)

    def __repr__(self):
        return 'bald.datetime.time({}, {}, {}, {})'.format(self.hour,
                                                            self.minute,
                                                            self.second, ms)

    def __add__(self, other):
        if not isinstance(other, timedelta):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if other.quantity == 'seconds':
            hours = self.hour + int(other.value) // 3600
            minutes = (int(other.value) % 3600) // 60
            seconds = (other.value % 3600) % 60
        elif other.quantity == 'minutes':
            hours = self.hour + int(other.value) // 60
            minutes = int(other.value) % 60
            seconds = self.seconds
        elif other.quantity == 'hours':
            hours = self.hour + other.value
            minutes = self.minute
            seconds = self.second
        if hours > 24:
            hours = hours % 24
        newtime = time(hours, minutes, seconds)
        return newtime


class datetime(object):
    """
    An idealized instant within a calendar, a combination of a
    :class:`bald.datetime.date` and a :class:`bald.datetime.time`.

    Attributes: year, month, day, hour, minute, second, microsecond,
    tzinfo and calendar.

    Objects of this type are not immutable.

    """
    def __init__(self, year, month, day, hour=0, minute=0, second=0,
                 microsecond=0, tzinfo=None, calendar=None, tsep='T'):

        # Design question: validate inputs?
        self.date = date(year, month, day, calendar)
        self.time = time(hour, minute, second, microsecond, tzinfo)
        self.tsep = tsep

    def __str__(self):
        return '{}{}{}'.format(str(self.date), self.tsep, str(self.time))

    def __repr__(self):
        return 'bald.datetime({})'.format(str(self))

    def __lt__(self, other):
        if not isinstance(other, datetime):
            msg = "unsupported operand type(s) for <: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        result = False
        if self.date < other.date:
            result = True
        elif self.date == other.date:
            if self.time.hour < other.time.hour:
                result = True
            elif self.time.hour == other.time.hour:
                if self.time.minute < other.time.minute:
                    result = True
                elif self.time.minute == other.time.minute:
                    if self.time.second < other.time.second:
                        result = True
        return result

    def __le__(self, other):
        if not isinstance(other, datetime):
            msg = "unsupported operand type(s) for <=: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        return self.__lt__(other) or self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, datetime):
            msg = "unsupported operand type(s) for =: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        datee = self.date == other.date
        houre = self.hour == other.hour
        minutee = self.minute == other.minute
        seconde = self.second == other.second
        return datee and houre and minutee and seconde

    def __ne__(self, other):
        if not isinstance(other, datetime):
            msg = "unsupported operand type(s) for !+: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        return not self == other

    def __gt__(self, other):
        if not isinstance(other, datetime):
            msg = "unsupported operand type(s) for >: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        result = False
        if self.date > other.date:
            result = True
        elif self.date == other.date:
            if self.time.hour > other.time.hour:
                result = True
            elif self.time.hour == other.time.hour:
                if self.time.minute > other.time.minute:
                    result = True
                elif self.time.minute == other.time.minute:
                    if self.time.second > other.time.second:
                        result = True
        return result

    def __ge__(self, other):
        if not isinstance(other, datetime):
            msg = "unsupported operand type(s) for >=: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        if not self.calendar == other.calendar:
            raise NotImplementedError('{} != {}'.format(self.calendar,
                                                        other.calendar))
        return self.__gt__(other) or self.__eq__(other)

    def __sub__(self, other):
        return CalendarDuration(self, other)

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def day(self):
        return self.date.day

    @property
    def calendar(self):
        return self.date.calendar

    @property
    def hour(self):
        return self.time.hour

    @property
    def minute(self):
        return self.time.minute

    @property
    def second(self):
        return self.time.second

    @property
    def microsecond(self):
        return self.time.microsecond

    @property
    def tzinfo(self):
        return self.time.tzinfo

    def __add__(self, other):
        if not isinstance(other, timedelta):
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        elif (type(other.value) == float and other.quantity not in
              ['seconds', 'microseconds']):
            msg = ('addition of floating point temporal quantities to '
                   'datetimes is not supported, results are ambiguous')
            raise TypeError(msg)
        if self.calendar is None:
            calendar = GregorianNoLeapSecond()
        else:
            calendar = self.calendar

        result = ''
        if other.value is None:
            result = None

        elif other.quantity in ['years', 'months', 'days']:
            newdate = self.date + other

            newtime = self.time
        elif other.quantity == 'seconds':
            naive_days = int(other.value) // (24 * 60 * 60)
            newdate = self.date + timedelta(days=naive_days)
            remainder = other.value % (24 * 60 * 60)
            for day, month, year in calendar.leapsecond_datetimes:
                leap_second_date = date(year, month, day, calendar=calendar)
                if leap_second_date > self.date and leap_second_date < newdate:
                    remainder -= 1
            newtime = self.time + timedelta(seconds=remainder)
            if newtime.hour < 0:
                newdate = newdate - timedelta(days=1)
                newtime.hour += 24
        elif other.quantity == 'minutes':
            pass
        elif other.quantity == 'hours':
            naive_days = int(other.value) // 24
            newdate = self.date + timedelta(days=naive_days)
            remainder = other.value % 24
            newtime = self.time + timedelta(hours=remainder)
            if newtime.hour < 0:
                newdate = newdate - timedelta(days=1)
                newtime.hour += 24
            
        else:
            raise ValueError('A timedelta with   cannot be '
                             'added to a datetime.')
        if result is not None:
            result = datetime(newdate.year, newdate.month, newdate.day,
                              newtime.hour, newtime.minute, newtime.second,
                              tzinfo=newtime.tzinfo,
                              calendar=self.calendar, tsep=self.tsep)
        return result


def convert_datetimes(datetimes):
    """
    Return a datetime or array of datetimes which may have been python
    `datetime.datetime` instances.

    """
    def _datetime_conversion(adt):
        if isinstance(adt, datetime):
            result = datetime
        elif (hasattr(adt, 'year') and hasattr(adt, 'month') and
              hasattr(adt, 'day') and hasattr(adt, 'hour') and
              hasattr(adt, 'minute') and hasattr(adt, 'second') and
              hasattr(adt, 'microsecond') and hasattr(adt, 'tzinfo')):
            result = datetime(adt.year, adt.month, adt.day, adt.hour,
                              adt.minute, adt.second,
                              tzinfo=adt.tzinfo,
                              calendar=GregorianNoLeapSecond())
        else:
            msg = 'cannot return datetime from {}'.format(str(datetime))
            raise TypeError(msg)
        return result
    if isinstance(datetimes, np.ndarray):
        pass
    else:
        result = _datetime_conversion(datetimes)
    return result


class CalendarDuration(object):
    """
    Represents a temporal period between two date or two datetime instances.

    The calendars of the two date or datetime instances must
    match.
    If both calendars are None, a GregorianNoLeapSecond
    calendar is assumed.  This is intended to give consistent results
    with Python's datetime module in most cases.

    """
    def __init__(self, end, start):
        if start.calendar != end.calendar:
            raise ValueError('CalendarDurations are not well defined across '
                             'differing calendars for '
                             'bald.datetime instances.')
        if start.calendar is None:
            self.calendar = GregorianNoLeapSecond()
        else:
            self.calendar = start.calendar
        self.start = start
        self.end = end

    # @property
    # def resolution(self):
        # return another time delta

    @property
    def years(self):
        """Return the length of time, floored to the nearest year."""
        if self.start.year is None or self.end.year is None:
            result = None
        else:
            result = self.end.year - self.start.year
            if self.end.month < self.start.month:
                if not self.end.day < self.start.day:
                    result -= 1
        return result

    # @property
    # def months(self):
    #     # requires that calendars are not None and number of months per year
    #     if self.start.year is None or self.end.year is None:
    #         result = None
    #     else:
    #         result = self.end.year - self.start.year
    #     return result

    @property
    def days(self):
        """Return the floor of the number of days."""
        def _add_day(adate, days):
            adate = adate + timedelta(days=1)
            days += 1
            if (self.calendar.is_leap_year(adate.year) and
               adate.month == self.calendar.leap_year_date.month and
               adate.day == (self.calendar.leap_year_date.day - 1)):
                days += 1
                adate = adate + timedelta(days=1)
            return adate, days

        if self.start.day is None or self.end.day is None:
            result = None
        else:
            # Accumulate to calculate
            adate = copy.copy(self.start)
            days = 0
            if (self.start.year == self.end.year and
               self.start.month == self.end.month):
                for d in range(self.start.day, self.end.day):
                    adate, days = _add_day(adate, days)
            else:
                # Handle the first month, which may be partial.
                mlen = self.calendar.month_day_map[self.start.month - 1]
                for d in range(mlen)[self.start.day:]:
                    adate, days = _add_day(adate, days)
                if self.end.year == self.start.year:
                    if self.end.month - self.start.month > 1:
                        for month_length in self.calendar.month_day_map[self.start.month:self.end.month - 1]:
                            for d in range(month_length):
                                adate, days = _add_day(adate, days)
                else:
                    # handle up to the end of the first year.
                    for month_length in self.calendar.month_day_map[self.start.month:]:
                        for d in range(month_length):
                            adate, days = _add_day(adate, days)
                    # Handle all the middle (full) years.
                    for year in range(self.end.year - self.start.year - 1):
                        for month_length in self.calendar.month_day_map:
                            for d in range(month_length):
                                adate, days = _add_day(adate, days)
                    # Handle the last year, which may be partial.
                    for month_length in self.calendar.month_day_map[:self.end.month - 1]:
                        for d in range(month_length):
                            adate, days = _add_day(adate, days)
                # Handle the last month, which may be partial.
                for d in range(self.calendar.month_day_map[self.end.month])[:self.end.day]:
                    adate, days = _add_day(adate, days)
            result = days
        return result

    def total_hours(self):
        if self.start.hour is None or self.end.hour is None:
            result = None
        else:
            hours = self.end.hour - self.start.hour
            result = self.days * 24 + hours
        return result

    def total_minutes(self):
        if self.start.minute is None or self.end.minute is None:
            result = None
        else:
            minutes = self.end.minute - self.start.minute
            result = self.total_hours() * 60 + minutes
        return result

    @property
    def seconds(self):
        if self.start.second is None or self.end.second is None:
            result = None
        else:
            seconds = self.end.second - self.start.second
            result = self.total_minutes() * 60 + seconds
        if False:
            # handle leap seconds if they exist within the period
            leapseconds = 0
            result += 1 * leapseconds

        return result

    def total_seconds(self):
        tsec = self.seconds
        if tsec is not None and self.microseconds is not None:
            result = self.seconds + self.microseconds
        return result

    @property
    def microseconds(self):
        if self.start.microsecond is None or self.end.microsecond is None:
            result = None
        else:
            result = self.end.microsecond - self.start.microsecond
        return result


class tzinfo(object):
    """
    An abstract base class for time zone information objects.
    These are used by the datetime and time classes to provide a customizable
    notion of time adjustment (for example, to account for time zone and/or
    daylight saving time).

    Objects of this type are not immutable.

    """
    pass


class timedelta(object):
    """this is a one of http://w3c.github.io/sdw/time/#time:Duration"""
    def __init__(self, days=None, seconds=None, microseconds=None, years=None,
                 months=None, hours=None, minutes=None):
        anames = ['days', 'seconds', 'microseconds', 'years',
                  'months', 'hours', 'minutes']
        attrs = [days, seconds, microseconds, years,
                 months, hours, minutes]
        if attrs.count(None) != len(attrs) -1:
            n = len(attrs) - attrs.count(None)
            raise ValueError('A timedelta must be initialised with one and '
                             'only one argument, {} given.\n'.format(n))
        
        (self.quantity, self.value), = [(aname, anattr) for aname, anattr in
                                        zip(anames, attrs)
                                        if anattr is not None]
        if isinstance(self.value, numpy.ma.core.MaskedConstant):
            self.value = None

    def total_seconds(self):
        return None


# class DateDuration(Duration):
#     """
#     A datetime duration, represented by whole unit like quantities.

#     For example 'April, 2012, ISO-Gregorian' is the whole month of April
#     with respect to the ISO-Gregorian Calendar.

#     Elements may be None, in which case the duration refers to any value
#     for that element.

#     """
#     def __init__(self, year=None, month=None, day=None, calendar=None):
#         self.year = year
#         self.month = month
#         self.day = day
#         self.calendar = calendar

#     def __sub__(self, other):
#         return Duration(self, other)


# class TimeDuration(Duration):
#     """
#     A datetime duration, represented by whole unit like quantities.

#     For example 'April, 2012, ISO-Gregorian' is the whole month of April
#     with respect to the ISO-Gregorian Calendar.

#     Elements may be None, in which case the duration refers to any value
#     for that element.

#     """
#     def __init__(self, hour=None, minute=None, second=None):
#         self.hour = hour
#         self.minute = minute
#         self.second = second

#     def __sub__(self, other):
#         return Duration(self, other)


# class SegmentedDuration(object):
#     """
#     A datetime duration, represented by collections of unit like quantities.
#     The duration may be segmented, for example: particular months within
#     particular years.

#     All defined elements match.

#     """
#     def __init__(self, year=None, month=None, day=None, hour=None,
#                  calendar=None):
#         self.years = year
#         self.months = month
#         self.days = day
#         self.hours = hour
#         self.calendar = calendar

class IntegerDatetimeOffsets(object):
    """
    A datetime offset array, an integer number of whole temporal unit
    quantities.

    """
    def __init__(self, offsets, unit):
        # Check this is a numpy array of integers.
        if isinstance(offsets, int):
            offsets = np.array((offsets,))
        elif isinstance(offsets, float):
            offsets = np.array((offsets,))
        self.offsets = offsets
        if not isinstance(unit, units.TemporalUnit):
            unit = units.TemporalUnit(unit)
        self.unit = unit


class EpochDateTimes(object):
    """
    An collection of instants within a calendar,
    offsets from a defined :class:`datetime` epoch with respect to
    its calendar.

    """
    def __init__(self, offsets, unit, epoch):
        """
        Create an EpochDateTimes instance.

        Args:

            * offsets - a numpy array, masked array or array like object
            * unit - the temporal unit
            * datetime - a :class:`bald.datetime.datetime` instance

        """
        self.offsets = IntegerDatetimeOffsets(offsets, unit)
        self.epoch = epoch

    @property
    def calendar(self):
        return self.epoch.calendar

    def __str__(self):
        dts = self.datetimes()
        result = str(dts)
        if not self.offsets.offsets.shape or len(dts) == 1:
            if not np.ma.is_masked(dts):
                result = str(dts[0])
        return result

    def datetimes(self):
        """
        Return an array of bald.datetime.datetime objects,
        or the offsets array if there are problems with deriving
        datetimes.
        """
        if not self.offsets.offsets.shape:
            offsets = self.offsets.offsets.reshape((1,))
        else:
            offsets = self.offsets.offsets
        if np.issubdtype(self.offsets.offsets.dtype, np.integer):
            result = np.array([str(self.epoch +
                                   timedelta(**{self.offsets.unit.unit: v}))
                               for v in offsets])
        else:
            result = self.offsets.offsets
        return result

    def __repr__(self):
        return self.__str__()


class Calendar(object):
    """
    A representation of the relationship between the different elements
    of a potential datetime instance.

    This includes the definition of periodic and nested
    unit like quantities.

    """
    def __init__(self, url=None,
                 leap_year_date=None,
                 month_names=None,
                 month_day_map=None, leapsecond_datetimes=None,
                 weekday_names=None,
                 weekday_start_date=None, null_years=None):
        self.url = url
        self.leap_year_date = leap_year_date
        if month_names is None:
            month_names = []
        self.month_names = month_names
        if len(month_names) != len(month_day_map):
            raise ValueError('month names:\n{}\nis not the same length as '
                             'month_day_map:\n'
                             '{}\n'.format(month_names, month_day_map))
        self.month_day_map = month_day_map
        if leapsecond_datetimes is None:
            leapsecond_datetimes = []
        self.leapsecond_datetimes = leapsecond_datetimes
        if weekday_names is None:
            weekday_names = []
        self.weekday_names = weekday_names
        self.weekday_start_date = weekday_start_date
        if null_years is None:
            null_years = []
        self.null_years = null_years

    def is_leap_year(self, year):
        """Return True for leap years, False for non-leap years."""
        return False

    @property
    def days_in_week(self):
        return len(self.weekday_names)

    @property
    def months_in_year(self):
        return len(self.month_names)

    @property
    def days_in_year(self):
        return sum(self.month_day_map)

    @property
    def days_in_leap_year(self):
        return None

    def is_valid_year(self, year):
        result = True
        if year in self.null_years:
            result = False
        return result

    def __eq__(self, other):
        return isinstance(self, type(other))

    def __ne__(self, other):
        return not self.__eq__(other)


class G360Day(Calendar):
    def __init__(self):
        url = None
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November',
                       'December']
        month_day_map = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]

        # leapsecond_datetimes = None
        # weekday_names = None
        # weekday_start_date = None
        # null_years = None
        super(G360Day, self).__init__(url, month_names=month_names,
                                      month_day_map=month_day_map)


class G365Day(Calendar):
    def __init__(self):
        url = None
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November',
                       'December']
        
        month_day_map = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        # leapsecond_datetimes = None
        # weekday_names = None
        # weekday_start_date = None
        # null_years = None
        super(G365Day, self).__init__(url, month_names=month_names,
                                      month_day_map=month_day_map)


class GregorianNoLeapSecond(Calendar):
    def __init__(self):
        url = None

        leap_year_date = date(None, 2, 29)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November',
                       'December']
        month_day_map = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        leapsecond_datetimes = None
        weekday_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                         'Thursday', 'Friday', 'Saturday']
        weekday_start_date = date(1995, 1, 1)
        null_years = [0]
        super(GregorianNoLeapSecond, self).__init__(url, leap_year_date,
                                                    month_names,
                                                    month_day_map,
                                                    leapsecond_datetimes,
                                                    weekday_names,
                                                    weekday_start_date,
                                                    null_years)

    def is_leap_year(self, year):
        """Return True for leap years, False for non-leap years."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @property
    def days_in_leap_year(self):
        return self.days_in_year + 1


class ISOGregorian(GregorianNoLeapSecond):
    def __init__(self):
        super(ISOGregorian, self).__init__()
        self.leapsecond_datetimes = self.get_ietf_leap_seconds()

    def get_ietf_leap_seconds(self):
        ietf_uri = 'https://www.ietf.org/timezones/data/leap-seconds.list'
        static = ('2272060800	10	# 1 Jan 1972\n'
                  '2287785600	11	# 1 Jul 1972\n'
                  '2303683200	12	# 1 Jan 1973\n'
                  '2335219200	13	# 1 Jan 1974\n'
                  '2366755200	14	# 1 Jan 1975\n'
                  '2398291200	15	# 1 Jan 1976\n'
                  '2429913600	16	# 1 Jan 1977\n'
                  '2461449600	17	# 1 Jan 1978\n'
                  '2492985600	18	# 1 Jan 1979\n'
                  '2524521600	19	# 1 Jan 1980\n'
                  '2571782400	20	# 1 Jul 1981\n'
                  '2603318400	21	# 1 Jul 1982\n'
                  '2634854400	22	# 1 Jul 1983\n'
                  '2698012800	23	# 1 Jul 1985\n'
                  '2776982400	24	# 1 Jan 1988\n'
                  '2840140800	25	# 1 Jan 1990\n'
                  '2871676800	26	# 1 Jan 1991\n'
                  '2918937600	27	# 1 Jul 1992\n'
                  '2950473600	28	# 1 Jul 1993\n'
                  '2982009600	29	# 1 Jul 1994\n'
                  '3029443200	30	# 1 Jan 1996\n'
                  '3076704000	31	# 1 Jul 1997\n'
                  '3124137600	32	# 1 Jan 1999\n'
                  '3345062400	33	# 1 Jan 2006\n'
                  '3439756800	34	# 1 Jan 2009\n'
                  '3550089600	35	# 1 Jul 2012\n'
                  '3644697600	36	# 1 Jul 2015\n'
                  '3692217600	37	# 1 Jan 2017\n')
        try:
            res = requests.get(ietf_uri)
            if res.status_code != 200:
                instr = static
            instr = res.text.split('\n')
        # requests.packages.urllib3.exceptions.MaxRetryError:
        except Exception:
            instr = static.split('\n')

        leap_years = []
        for line in instr:
            if line and not line.startswith('#'):
                day, month, year = line.split('#')[1].split(' ')[1:4]
                leap_years.append((int(day), month, int(year)))
        return leap_years
