
from math import radians, sin, cos, sqrt, atan2, exp
from typing import List

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def calculate_list_overlap(list1: List[str], list2: List[str]) -> float:
    if not list1 or not list2:
        return 0.0
    s1 = set([x.lower().strip() for x in list1])
    s2 = set([x.lower().strip() for x in list2])
    inter = len(s1 & s2)
    uni = len(s1 | s2)
    return inter / uni if uni else 0.0

def distance_score(distance_km: float, max_distance_km: float) -> float:
    return max(0.0, min(100.0, 100.0 * exp(- distance_km / (max_distance_km / 3))))
