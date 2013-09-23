from .api import register, make_forwarder

def includeme(config):
    from . import views
    
    """
    Pass this to your configurator object like so:
    
    from . import nimblescan
    config.include(nimblescan, route_prefix="nimblescan")
    """
    
    # Standard views
    config.add_route('nimblescan.list', '/list')
    config.add_route('nimblescan.flush', '/flush')
    config.add_route('nimblescan.action', '/action')
    
    # Now link the views
    config.add_view(views.generate_list, route_name='nimblescan.list', renderer='string', permission='loggedin')
    config.add_view(views.flush, route_name='nimblescan.flush', renderer='string', permission='loggedin')
    config.add_view(views.action, route_name='nimblescan.action', permission='loggedin')
    
    register('nimblescan.flush', "Refresh scan menu", ['nimblescan'], (lambda r: True), make_forwarder("nimblescan.flush"))
    
    return config
