import json
from datetime import datetime
from decimal import Decimal

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")