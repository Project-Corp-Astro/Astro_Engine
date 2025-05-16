import swisseph as swe
from datetime import datetime, timedelta
import logging
import math

# Constants
PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
NAKSHATRA_LIST = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']

# Logger
logger = logging.getLogger(__name__)

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day (UTC)."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
    logger.debug(f"Julian Day: {jd:.6f}")
    return jd

def calculate_sidereal_position(jd, planet_id, ayanamsa):
    """Calculate sidereal longitude and retrograde status of a planet."""
    pos, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    sidereal_lon = (pos[0] - ayanamsa) % 360
    speed = pos[3]  # Speed in longitude
    retrograde = 'R' if speed < 0 else ''
    return sidereal_lon, retrograde

def calculate_ascendant(jd, lat, lon):
    """Calculate sidereal Ascendant longitude using Whole Sign system."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    logger.debug(f"Sidereal Ascendant Longitude: {asc_lon:.6f}")
    return asc_lon

def get_sign_and_degrees(longitude):
    """Extract sign and degrees within the sign from longitude."""
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    sign = SIGNS[sign_index]
    return sign, degrees

def calculate_d7_sign(longitude, natal_sign):
    """Calculate D7 (Saptamsa) sign based on natal longitude and sign."""
    is_odd = SIGNS.index(natal_sign) % 2 == 0
    if is_odd:
        start_sign = natal_sign
    else:
        start_sign = SIGNS[(SIGNS.index(natal_sign) + 6) % 12]  # 7th sign from natal sign
    degrees = longitude % 30
    saptamsa_number = math.ceil(degrees / (30 / 7))
    d7_sign_index = (SIGNS.index(start_sign) + saptamsa_number - 1) % 12
    d7_sign = SIGNS[d7_sign_index]
    return d7_sign

def calculate_d7_house(d7_sign, d7_asc_sign):
    """Calculate house number using Whole Sign system with D7 Ascendant."""
    d7_sign_index = SIGNS.index(d7_sign)
    d7_asc_index = SIGNS.index(d7_asc_sign)
    house = (d7_sign_index - d7_asc_index + 12) % 12 + 1
    return house

def get_nakshatra_pada(longitude):
    """Calculate nakshatra and pada from sidereal longitude."""
    longitude = longitude % 360
    pada_index = int(longitude / (360 / 108))  # 108 padas in 360 degrees
    nakshatra_index = pada_index // 4
    pada = (pada_index % 4) + 1
    nakshatra_name = NAKSHATRA_LIST[nakshatra_index]
    return nakshatra_name, pada

def raman_saptamsha(jd, lat, lon):
    """Calculate D7 chart data with retrograde status, nakshatras, and padas."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    logger.debug(f"Raman Ayanamsa: {ayanamsa:.6f}")

    # Calculate natal Ascendant and its D7 position
    asc_lon = calculate_ascendant(jd, lat, lon)
    natal_asc_sign, asc_degrees = get_sign_and_degrees(asc_lon)
    d7_asc_sign = calculate_d7_sign(asc_lon, natal_asc_sign)
    asc_nakshatra, asc_pada = get_nakshatra_pada(asc_lon)

    # Calculate planetary positions in D7 chart
    planets = {}
    for planet_name in PLANET_NAMES:
        if planet_name == 'Rahu':
            planet_id = swe.MEAN_NODE
            lon, retrograde = calculate_sidereal_position(jd, planet_id, ayanamsa)
            retrograde = 'R'  # Rahu is always retrograde
        elif planet_name == 'Ketu':
            planet_id = swe.MEAN_NODE
            lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
            lon = (lon + 180) % 360  # Ketu is 180° opposite Rahu
            retrograde = 'R'  # Ketu is always retrograde
        else:
            planet_id = getattr(swe, planet_name.upper())
            lon, retrograde = calculate_sidereal_position(jd, planet_id, ayanamsa)

        natal_sign, degrees = get_sign_and_degrees(lon)
        d7_sign = calculate_d7_sign(lon, natal_sign)
        house = calculate_d7_house(d7_sign, d7_asc_sign)
        nakshatra, pada = get_nakshatra_pada(lon)

        planets[planet_name] = {
            "natal_sign": natal_sign,
            "degrees": round(degrees, 6),
            "retrograde": retrograde,
            "d7_sign": d7_sign,
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada
        }

    # Add Ascendant to the chart
    planets['Ascendant'] = {
        "natal_sign": natal_asc_sign,
        "degrees": round(asc_degrees, 6),
        "retrograde": "",
        "d7_sign": d7_asc_sign,
        "house": 1,
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    return planets