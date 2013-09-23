from sqlalchemy import or_, func
from .config import config
from datetime import datetime, timedelta
from .models import NimblescanCache
from collections import defaultdict
import json

def flush(user_id):
    return config['DBSession'].query(NimblescanCache).filter(NimblescanCache.user == user_id).delete()

def get(user_id, allow_expired=False):
    r = config['DBSession'].query(NimblescanCache).filter(
        NimblescanCache.user == user_id,
    ).first()
    
    if r is None:
        return None
    
    if r.expires < datetime.now() and not allow_expired:
        return None
    
    return r

def build(request):
    now = datetime.now()
    
    options = defaultdict(list)
    for h in config['handlers'].values():
        if h.qualifier(request):
            options[h.label].append(h)
    
    k_list = list(options.keys())
    k_list.sort()
    
    result = []
    for key in k_list:
        for h in options[key]:
            result.append([h.name, h.label, h.search_terms])
    
    return json.dumps(result)

def cache(content, user_id):
    flush(user_id)
    
    new_cache = NimblescanCache(
        user    = user_id,
        expires = datetime.now() + timedelta(hours=24),
        content = content,
    )
    return config['DBSession'].add(new_cache)
