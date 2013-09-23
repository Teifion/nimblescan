import datetime
from pyramid.response import Response

from pyramid.httpexceptions import HTTPFound

from pyramid.renderers import render_to_response

from . import api
from .config import config
from . import lib

def generate_list(request):
    request.do_not_log = True
    the_user = config['get_user_func'](request)
    
    the_list = lib.get(the_user.id)
    
    if the_list != None:
        return Response(body=the_list.content, content_type='application/json')
    
    new_list = lib.build(request)
    lib.cache(new_list, the_user.id)
    
    return Response(body=new_list, content_type='application/json')

def flush(request):
    """
    Wipe the cache for a given user
    """
    request.do_not_log = True
    user_id = config['get_user_func'](request).id
    lib.flush(user_id)
    
    if "fwd" in request.params:
        return HTTPFound(location=request.params['fwd'])
    return HTTPFound(location=request.route_url('/'))

def action(request):
    request.do_not_log = True
    # the_user = config['get_user_func'](request)
    
    handler_name = request.params['n'].strip()
    if handler_name not in config['handlers']:
        raise Exception("No handler by that name")
    
    handler = config['handlers'][handler_name].handler
    return handler(request)
