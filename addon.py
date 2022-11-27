import sys
import xbmc
import xbmcaddon
import xbmcgui
import json
from datetime import datetime, timedelta, time


def convert_time(runtime):
    addon = xbmcaddon.Addon()
    if addon.getSetting('day_display') == 'false':
        return '{0} days {1} hours {2} minutes'.format(int(runtime/24/60), int(runtime/60%24), f'{runtime%60:.2f}')
    else:
        return '{0} hours {1} minutes'.format(int(runtime/60), f'{runtime%60:.2f}')

def display_details(addon, show_title, message):
    addon_name = addon.getAddonInfo('name')
    xbmcgui.Dialog().ok('{0} - {1}'.format(addon_name, show_title), message)
    
def get_end_time(current_time_finish):
    current_time_finish = datetime.now() + timedelta(seconds=finish_runtime)
    return (current_time_finish)    

if __name__ == '__main__':
    addon = xbmcaddon.Addon()
    remaining_runtime, finish_runtime, total_runtime = 0,0, 0
    query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "filter": { "field": "title", "operator": "is", "value": "" }, "limits": { "start": 0, "end": 1}, "properties": [ "title", "originaltitle", "playcount", "episode", "episodeguide", "watchedepisodes", "season"], "sort": { "order": "ascending", "method": "label"} }, "id": "libTvShows"}
    query = json.loads(json.dumps(query))
    query['params']['filter']['value'] = sys.listitem.getLabel()
    response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
    
    if response['result']['limits']['total'] > 0:
        show_id = response['result']['tvshows'][0]['tvshowid']
        show_title = response['result']['tvshows'][0]['title']
        total_seasons = response['result']['tvshows'][0]['season']
        total_episodes = response['result']['tvshows'][0]['episode']
        watched_episodes = response['result']['tvshows'][0]['watchedepisodes']
        
        query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "filter": { "field": "tvshow", "operator": "is", "value": "" }, "limits": { "start" : 0, "end": total_episodes }, "properties": ["playcount", "runtime", "tvshowid"], "sort": { "order": "ascending", "method": "label" } }, "id": "libTvShows"}
        query = json.loads(json.dumps(query))
        query['params']['filter']['value'] = show_title
        response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
        
        for episode in response['result']['episodes']:
            if episode['playcount'] == 0:
                remaining_runtime += episode['runtime'] / 60
                finish_runtime += episode['runtime']
            total_runtime += episode['runtime'] / 60
        
        xbmc.log('Context Showruntime remaining runtime: ' + str(show_title) + ' ' + str(remaining_runtime), xbmc.LOGDEBUG)
        xbmc.log('Context Showruntime total runtime: ' + str(show_title) + ' ' + str(total_runtime), xbmc.LOGDEBUG)

        remaining_runtime = convert_time(remaining_runtime)
        finish_runtime = get_end_time(finish_runtime)
        total_runtime = convert_time(total_runtime)

        xbmc.log('Context Showruntime remaining runtime converted: ' + str(show_title) + ' ' + str(remaining_runtime), xbmc.LOGDEBUG)
        xbmc.log('Context Showruntime total runtime converted: ' + str(show_title) + ' ' + str(total_runtime), xbmc.LOGDEBUG)
       
        if addon.getSetting('detailed_info') == 'true':
            percent = '{0}%'.format(str(round((float(watched_episodes)/total_episodes) * 100))[:-2])
            message = 'Watched/Unwatched: {0}/{1} ({2})'.format(watched_episodes, total_episodes, percent)
            message = '{0}\nRemaining runtime: {1}'.format(message, remaining_runtime)
            message = '{0}\nFinish runtime: {1}'.format(message, finish_runtime)[:-7]
            message = '{0}\nTotal runtime: {1}'.format(message, total_runtime)
            display_details(addon, show_title, message)
        else:
            xbmc.executebuiltin("Notification(Remaining runtime - {0}, {1})".format(show_title, remaining_runtime))