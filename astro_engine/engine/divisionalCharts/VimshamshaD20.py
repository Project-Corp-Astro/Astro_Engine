import swisseph as swe
from datetime import datetime, timedelta
import math

# Zodiac signs list
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Convert birth date, time, and timezone offset to Julian Day (UT).
    
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format
        time_str (str): Birth time in 'HH:MM:SS' format
        tz_offset (float): Timezone offset in hours (e.g., 5.5 for IST)
    
    Returns:
        float: Julian Day in Universal Time
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def format_dms(degrees):
    """
    Format longitude in degrees, minutes, seconds (e.g., '17°41'36"').
    
    Args:
        degrees (float): Decimal degrees
    
    Returns:
        str: Formatted string in DMS
    """
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}°{m}'{s:.1f}\""

def get_d20_position(sidereal_lon):
    """
    Calculate D20 sign from sidereal longitude.
    
    Args:
        sidereal_lon (float): Sidereal longitude in degrees (0-360)
    
    Returns:
        dict: D20 sign and its index (0-11)
    """
    natal_sign_index = int(sidereal_lon // 30) % 12  # Sign index in natal chart (0-11)
    degrees_in_sign = sidereal_lon % 30              # Degrees within the sign
    segment_number = math.floor(degrees_in_sign / 1.5)  # Segment number (0-19, 1.5° each)
    
    # D20 sign calculation: Maps the segment to a new sign
    d20_sign_index = (natal_sign_index * 20 + segment_number) % 12
    d20_sign = SIGNS[d20_sign_index]
    return {'sign': d20_sign, 'sign_index': d20_sign_index}

def get_d20_house(planet_d20_sign_index, d20_asc_sign_index):
    """
    Assign house number using Whole Sign system.
    
    Args:
        planet_d20_sign_index (int): D20 sign index of the planet (0-11)
        d20_asc_sign_index (int): D20 ascendant sign index (0-11)
    
    Returns:
        int: House number (1-12)
    """
    return (planet_d20_sign_index - d20_asc_sign_index) % 12 + 1

def calculate_d20_chart(birth_date, birth_time, latitude, longitude, tz_offset):
    """
    Calculate the D20 (Vimsamsa) chart based on birth details.
    
    Args:
        birth_date (str): Birth date in 'YYYY-MM-DD' format
        birth_time (str): Birth time in 'HH:MM:SS' format
        latitude (float): Latitude of birth place
        longitude (float): Longitude of birth place
        tz_offset (float): Timezone offset in hours
    
    Returns:
        dict: D20 chart data including ascendant, planetary positions, and house signs
    """
    # Calculate Julian Day
    jd_ut = get_julian_day(birth_date, birth_time, tz_offset)

    # Set Lahiri Ayanamsa for sidereal calculations
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Calculate sidereal longitudes for planets
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED  # Sidereal + speed for retrograde detection

    d1_positions = {}
    for planet_id, name in planets:
        pos, _ = swe.calc_ut(jd_ut, planet_id, flag)
        lon = pos[0] % 360  # Normalize to 0-360°
        retro = 'R' if pos[3] < 0 else ''  # Check retrograde via speed
        d1_positions[name] = (lon, retro)

    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, '')  # Ketu is not retrograde by convention

    # Calculate ascendant sidereal longitude
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_lon = ascmc[0] % 360  # Ascendant longitude

    # Calculate D20 ascendant position
    d20_asc = get_d20_position(d1_asc_lon)
    d20_asc_sign_index = d20_asc['sign_index']

    # Calculate D20 positions for all planets
    d20_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d20_pos = get_d20_position(d1_lon)
        house = get_d20_house(d20_pos['sign_index'], d20_asc_sign_index)
        d20_positions[planet] = {
            "sign": d20_pos['sign'],
            "house": house,
            "retrograde": retro,
            "longitude": format_dms(d1_lon)
        }

    # Assign house signs using Whole Sign system
    house_signs = [
        {"house": i + 1, "sign": SIGNS[(d20_asc_sign_index + i) % 12]}
        for i in range(12)
    ]

    # Return chart data
    return {
        "d20_ascendant": {
            "sign": d20_asc['sign'],
            "longitude": format_dms(d1_asc_lon)
        },
        "planetary_positions": d20_positions,
        "house_signs": house_signs
    }