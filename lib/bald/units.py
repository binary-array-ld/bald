import re
import six

class BaseUnit(object):
    """The definition of a base unit of measure, with a scaling factor to
    convert to SI units."""
    ustring = 'UNIT'
    def __init__(self, unit, scaling):
        """
        Args:

            * unit - String
            * scaling - String

        """
        self.unit = unit
        self.scaling = scaling

    def __str__(self):
        return '{u}["{n}",{s}]'.format(u=self.ustring, n=self.unit,
                                       s=self.scaling)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        result = False
        if isinstance(other, BaseUnit):
            if self.unit == other.unit and self.scaling == other.scaling:
                result == True
        elif isinstance(other, six.string_types):
            if self.unit == other:
                result = True
        else:
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            msg = msg.format(type(self), type(other))
            raise TypeError(msg)
        return result

    def wktcrs(self, ind=0):
        pattern = '{ind}{u}["{n}",{s}]'
        result = pattern.format(ind=ind*'  ', u=self.ustring, n=self.unit,
                                s=self.scaling)
        return result

    @property
    def scaling_factor(self):
        """Floating point representation of the defined scaling factor to convert to SI units."""
        return float(self.scaling)

    wkt_pattern = re.compile('(?P<utype>\w+)\["(?P<ustr>[\w\s0-9\.\-]+)"\s*,\s*(?P<sfactor>[0-9\.]+)\]')

    @classmethod
    def parse_wktcrs(cls, wktcrs_string, strict=False):
        match = cls.wkt_pattern.match(wktcrs_string)
        unit = None
        if match:
            if match.group('utype') == AngleUnit.ustring:
                unit = AngleUnit(unit=match.group('ustr'), scaling=match.group('sfactor'))
            elif match.group('utype') == LengthUnit.ustring:
                unit = LengthUnit(unit=match.group('ustr'), scaling=match.group('sfactor'))
            elif match.group('utype') == TimeUnit.ustring:
                unit = TimeUnit(unit=match.group('ustr'), scaling=match.group('sfactor'))
        return unit


class AngleUnit(BaseUnit):
    """The definition of an angular unit of measure, with a scaling factor to convert to SI units: radians."""
    ustring = 'ANGLEUNIT'


class LengthUnit(BaseUnit):
    """The definition of an linear unit of measure, with a scaling factor to convert to SI units: metres."""
    ustring = 'LENGTHUNIT'

class TimeUnit(BaseUnit):
    """The definition of a time unit of measure, with a scaling factor to convert to SI units: seconds."""
    ustring = 'TIMEUNIT'

class TemporalUnit(BaseUnit):
    """
    The definition of a temporal unit of measure: a temporal unit shall always be used
    with respect to a calendar and may not be converted to SI units.

    """
    ustring = 'TEMPORALUNIT'
    def __init__(self, unit):
        scaling = None
        allowed_units = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
        if unit not in allowed_units:
            if unit + 's' in allowed_units:
                unit = unit + 's'
            else:
                raise ValueError('{} not one of the allowed units'.format(unit))
        super(TemporalUnit, self).__init__(unit, scaling)
        

class TemporalDecimalUnit(BaseUnit):
    """
    The definition of a temporal decimal unit of measure: a temporal decimal unit
    may not be converted to SI units and may not be converted to other temporal
    units via a calendar.

    Such temporal representations are useful for geology, geodesy and planetary representations.

    """
    ustring = 'TEMPORALDECIMALUNIT'
    def __init__(self, unit):
        scaling = None
        allowed_units = ['year', 'day']
        if unit not in allowed_units:
            raise ValueError('{} not one of the allowed units'.format(unit))
        super(TemporalUnit, self).__init__(unit, scaling)

