from collections import namedtuple
from .config import config
from . import lib
from pyramid.httpexceptions import HTTPFound
from urllib.parse import urlencode

def make_forwarder(path, **kwargs):
    def f(request):
        return HTTPFound(location=request.route_url(path, **kwargs))
    return f

def make_raw_forwarder(path):
    def f(request):
        return HTTPFound(location=path)
    return f

def make_form_forwarder(path, params, **kwargs):
    def  f(request):
        data = {}
        if params != []:
            for p in params:
                data[p] = request.params[p]
        else:
            data = dict(request.params)
        return HTTPFound(location=request.route_url(path, **kwargs) + "?{}".format(urlencode(data, True)))
    return f

def flush(user_id):
    """
    Calls lib.flush beacuse it's likely to be called outside of the module
    and thus it makes sense to allow it to be accessed from here
    """
    
    return lib.flush(user_id)

NimblescanLink = namedtuple("NimblescanLink", ["name", "label", "search_terms", "qualifier", "handler", "form_data"])
def register(name, label, search_terms, qualifier, handler, form_data="", raise_on_dupe=False):
    """
    Examples:
    api.register('wordy.menu', "Wordy - Menu", ['games'], (lambda r: True), api.make_forwarder("wordy.menu"))
    api.register('wordy.new_game', "Wordy - New game", ['games'], (lambda r: True), api.make_form_forwarder("wordy.new_game", []), '<label for="ns_opponent">Opponent:</label> <input type="text" name="opponent_name1" id="ns_opponent" value="" style="display:inline-block;"/>')
    api.register('wordy.stats', "Wordy - Stats", ['games'], (lambda r: True), api.make_forwarder("wordy.stats"))
    api.register('wordy.preferences', "Wordy - Preferences", ['games'], (lambda r: True), api.make_forwarder("wordy.preferences"))
    """
    
    if name in config['handlers']:
        if raise_on_dupe:
            raise KeyError("{} already exists".format(name))
        else:
            return False
    
    nc = NimblescanLink(name, label, search_terms + [label], qualifier, handler, form_data)
    config['handlers'][name] = nc
    return True

"""
    Javascript to insert into your HTML template
    
    <script type="text/javascript" charset="utf-8">
        var current_ns_selection = 0;
        var nimblescan_url = '${request.route_url('nimblescan.action')}';
        
        var ns_isCtrl = false;
        var ns_isShift = false;

        // Now you get to pick which key it is
        var ns_f_key = 70;
        var ns_p_key = 80;
        var ns_l_key = 76;
        
        var ns_down_arrow = 40;
        var ns_up_arrow = 38;
        var ns_enter = 13
        
        var ns_hotkey = ns_l_key;
        var ns_item_list = null;
        
        $(document).ready(function() {
            $('body').after('<div id="nimblescan_dialog" style="display:none;" title="">\
                <input type="text" id="nimblescan_text" value="" style="width:99%;"/>\
                <div id="nimblescan_list" style="max-height:' + ($(window).height()-300) + 'px;">\
                    &nbsp;\
                </div>\
            </div><div id="nimblescan_form" style="display:none;"></div><div id="nimblescan_cache" style="display:none;"></div>');
            
            $('#nimblescan_text').keyup(function(e) {
                if (e.which != ns_down_arrow && e.which != ns_up_arrow && e.which != ns_enter)
                {
                    update_nimblescan_modal(true);
                }
            });
            
            $('#nimblescan_text').keydown(function(e) {
                if(e.which == ns_enter) {
                    var search_term = $('#nimblescan_text').val().toLowerCase();
                    select_goto(search_term);
                    e.preventDefault();
                }
                else if(e.which == ns_down_arrow)
                {
                    current_ns_selection += 1;
                    update_nimblescan_modal(false);
                    e.preventDefault();
                }
                else if(e.which == ns_up_arrow)
                {
                    current_ns_selection -= 1;
                    if (current_ns_selection < 0)
                    {
                        current_ns_selection = 0;
                    }
                    update_nimblescan_modal(false);
                    e.preventDefault();
                }
            });

            // This is where we check to see if we bring up the window
            $(document).keyup(function(e) {
                if(e.which == 17) {
                    isCtrl = false;
                }
                if(e.which == 16) {
                    isShift = false;
                }
            });
            // action on key down
            $(document).keydown(function(e) {
                if(e.which == 17) {
                    isCtrl = true;
                }
                if(e.which == 16) {
                    isShift = true;
                }
                if(e.which == ns_hotkey && isCtrl && isShift) {
                    //alert(e.which);
                    show_nimblescan_modal();
                }
            });
            
            // When testing it can be useful to uncomment the following line
            // show_nimblescan_modal();
        });

        // This function performs the actual filtering
        /*
        It expects the items in the form:
        [name, label, [search_terms], use_modal]
        */
        function filter_gotos (search_term)
        {
            var found_items = [];
            
            var search_terms = search_term.toLowerCase().split(" ");
            
            // For each possible item we can go to
            for (var i = 0; i < ns_item_list.length; i++)
            {
                the_item = ns_item_list[i];
                use_this_item = false;
                
                // No search term? List all the items
                if (search_terms == [""]) {
                    use_this_item = true
                    continue;
                };
                
                // For each searchable term this item has
                var terms = the_item[2];
                for (var j = 0; j < terms.length; j++)
                {
                    if (use_this_item == true) {continue;}
                    
                    haystack = terms[j].toLowerCase();
                    contains_all_parts = true;
                    
                    // For each of our search terms
                    for (var k = 0; k < search_terms.length; k++)
                    {
                        if (search_terms[k] === "") {continue;}
                        if (haystack.indexOf(search_terms[k]) == -1)
                        {
                            contains_all_parts = false;
                        }
                    }
                    
                    if (contains_all_parts)
                    {
                        use_this_item = true;
                    }
                }
                
                if (use_this_item)
                {
                    found_items.push(the_item);
                }
            }
            
            return found_items;
        }
        
        function select_goto (search_term)
        {
            var found_items = filter_gotos(search_term);
            var name = found_items[current_ns_selection][0];
            var form = found_items[current_ns_selection][3];
            url = '${request.route_url('nimblescan.action')}';
            
            if (form == "")
            {
                document.location = url + '?n=' + name;
            }
            else
            {
                show_form_dialog(url, name, form);
            }
            
            /*
            May want to use this with a more complex form, leaving it in for future reference
            if (jQuery.isEmptyObject(form))
            {
                document.location = '${request.route_url('nimblescan.action')}?n=' + found_items[current_ns_selection][0];
            }
            else
            {
                alert("No handler");
            }
            */
        }
        
        function show_form_dialog (url, name, form_contents)
        {
            var output = '<form action="' + url + '" method="post" accept-charset="utf-8">\
                <input type="hidden" name="n" id="n" value="' + name + '" />\
                ' + form_contents + '\
                <input type="submit" id="nimblescan_submit" name="form.submitted" class="icbutton ui-button ui-widget ui-state-default ui-corner-all" value="Submit" style="margin: 0 auto;" role="button" aria-disabled="false">\
            <' + '/form>';
            
            $('#nimblescan_form').html(output);
            $('#nimblescan_form').dialog({
                modal:true,
                position:"top",
                minWidth: 600,
                closeOnEscape:true
            });
        }
        
        function build_nimblescan_list (search_term, reset)
        {
            if (reset) {current_ns_selection=0};
            
            var output = "";
            var found_items = filter_gotos(search_term);
            
            if (current_ns_selection >= found_items.length)
            {
                current_ns_selection = found_items.length-1;
            }
            
            output = "";
            
            for (var i = 0; i < found_items.length; i++)
            {
                the_item = found_items[i];

                if (i == current_ns_selection)
                {
                    bg_colour = "#7AF";
                }
                else
                {
                    bg_colour = "#EEE";
                }
                output += "<a hhref='" + nimblescan_url + "?n=" + the_item[0] + "' onclick='alert(\"You need to use the up and down arrows along with the enter key to select options\"); $(\"#nimblescan_text\").focus();' style='display:block; text-decoration:none;background-color:" + bg_colour + ";margin:1px -3px 1px 0px;padding:2px;'>" + the_item[1] + "</a>";
            }
            
            return output;
        }
        
        /*
        If we call this and it wraps a check around the actual showing to ensure
        we've got some links to show.
        */
        function show_nimblescan_modal ()
        {
            if (ns_item_list == null)
            {
                $.ajax({
                    url: '${request.route_url('nimblescan.list')}',
                    type: 'get',
                    async: false,
                    cache: false,
                    success: function(data) {
                        ns_item_list = data;
                        if (ns_item_list != [])
                        {
                            actually_show_nimblescan_modal();
                        }
                    }
                });
            }
            else
            {
                if (ns_item_list != "")
                {
                    actually_show_nimblescan_modal();
                }
            }
        }
        
        function actually_show_nimblescan_modal ()
        {
            $('#nimblescan_text').val("");
            $('#nimblescan_list').html("");
            search_term = "";
            var nimblescan_list = build_nimblescan_list(search_term, true);
            
            if (nimblescan_list != "")
            {
                $('#nimblescan_list').html(nimblescan_list);
                $('#nimblescan_dialog').dialog({
                    modal:true,
                    position:"top",
                    show: {
                        duration: 400,
                        effect: "fade",
                        easing: "swing"
                    },
                    closeOnEscape:true
                });
            }
        }
        
        function update_nimblescan_modal (reset)
        {
            search_term = $('#nimblescan_text').val().toLowerCase();
            var nimblescan_list = build_nimblescan_list(search_term, reset);
            
            $('#nimblescan_list').html(nimblescan_list);
        }
    </script>
"""