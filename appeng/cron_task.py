#!/usr/bin/env python

from django.conf import settings
import os, sys, django, logging
import urllib.request
import requests

logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    sys_path_to_add = r'D:\lee_shiueh\FLH\workspace\django_apps\cmstation\appeng'
else:
    sys_path_to_add = '/usr/share/appeng'
    #sys_path_to_add = '/home/pi/django/appeng'

#sys_path_to_add = os.path.dirname(os.path.dirname(os.getcwd()))
logger.debug('system path to add %s' % sys_path_to_add)
sys.path.append(sys_path_to_add)

os.environ['DJANGO_SETTINGS_MODULE'] = 'appeng.settings'
django.setup()

from coolmaster.models import CMUnitStat
from dbconfig.views import get_app_json_db_config

DEFAULT_CONFIG_CRON = {
                        'cms_stat_url': 'http://127.0.0.1/appeng/cmapi/stat/',
                        'hc2_vd_update_url': 'http://192.168.2.100/api/globalVariables/CM_Sync',
                        'hc2_account' : 'admin',
                        'hc2_passwd' : 'admin',
                       }

CM_STAT_TEST_DATAS = [
"""command execute: stat

stat
OK
>
>""",
"""command execute: stat

stat
100 OFF 18C 20,50C Low  Fan  OK
101 OFF 21C 19,20C Med  Cool OK
102 OFF 28C 18,10C Low  Dry  OK
103 ON  28C 23,50C Low  HExc OK
OK
>
>""",                     
                      ]

try:
    
    app_config = get_app_json_db_config(__name__,DEFAULT_CONFIG_CRON)
    url = app_config.get('cms_stat_url')
    logger.debug('get coolmaster stat from url: %s' % url)

    hc2_vd_update_url = app_config.get('hc2_vd_update_url')
    hc2_account = app_config.get('hc2_account')
    hc2_passwd = app_config.get('hc2_passwd')
    #hc2_vd_update_url = 'http://127.0.0.1:9000/hc2/update/'
    logger.debug('hc2_vd_update_url: %s' % hc2_vd_update_url)
    
    logger.debug('cms_stat_url: %s' % url)
    cm_data = urllib.request.urlopen(url).read().decode()
    #if '>' == cm_data[-1]:
    if True:
        has_changed = False
        lines = cm_data.split('\r\n')
        for line in lines:
            if len(line) > 30:
                logger.debug('get unit stat data: %s' % line)
                if CMUnitStat.is_unit_stat_changed(line):
                    logger.info('controlled unit %s stat changed' % line[:3])
                    has_changed = True
                else:
                    logger.debug('unit %s stat no change' % line[:3])
            else:
                logger.debug('ignore line data: %s' % line)
        if has_changed:
            logger.debug('hc2 auth with (%s,%s)' % (hc2_account,hc2_passwd))
            logger.debug('cm_data: %s' % str(cm_data))
            if not '127.0.0.1' in hc2_vd_update_url:
                hc2_resp = requests.put(hc2_vd_update_url,auth=(hc2_account,hc2_passwd),json={'value':cm_data})
                if hc2_resp.status_code != 200:
                    logger.warning('hc2 response: %s' % hc2_resp.content.decode())
                else:
                    logger.debug('hc2 CM_Sync variable updated')
            else:
                with urllib.request.urlopen(hc2_vd_update_url) as hc2_resp:
                    logger.debug('hc2 self simulation response: %s' % hc2_resp.read().decode())
        else:
            logger.debug('stat not changed')
    else:
        logger.info('response cm_data broken,\n %s\n try next time' % cm_data)
except:
    logger.error('cron task failed', exc_info = True)

