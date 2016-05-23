from django.db import models
import serial, os, logging

from dbconfig.views import get_app_json_db_config

logger = logging.getLogger(__name__)
# Create your models here.

DEFAULT_CONFIG_COOLMASTER = {
                  'port': '/dev/ttyUSB0',
                  'baudrate': 9600,
                  'parity' : serial.PARITY_NONE,
                  'stopbits' : serial.STOPBITS_ONE,
                  'bytesize' : serial.EIGHTBITS,
                  'timeout' : 0.5,
                  }


def get_coolmaster_instrument():
    app_config = get_app_json_db_config(__name__, DEFAULT_CONFIG_COOLMASTER)
    if os.path.exists(app_config['port']):
        instr = serial.Serial(
                              baudrate = app_config['baudrate'],
                              parity = app_config['parity'],
                              stopbits = app_config['stopbits'],
                              bytesize = app_config['bytesize'],
                              timeout = app_config['timeout'])
        instr.port = app_config['port']
    else:
        logger.warning('serial port is not exist! take it simulation mode')
    return instr

class CMUnitStat(models.Model):
    """
    """
    uid = models.CharField('UID',max_length=3,unique=True)
    status = models.CharField('Status',max_length=3)
    sett = models.CharField('Set Temperature',max_length=3)
    roomt = models.CharField('Room Temperature', max_length=6)
    fanspeed = models.CharField('Fan Speed',max_length=4)
    opmode = models.CharField('Operation Mode',max_length=4)
    ecode = models.CharField('Failure Code',max_length=4)
    
    @classmethod
    def is_unit_stat_changed(cls,unit_stat_data):
        logger.debug('param unit_stat_data: %s' % unit_stat_data)
        if len(unit_stat_data) < 30:
            logger.warning('param unit_stat_data %s error, ignored.' % unit_stat_data)
            return False
        uid = (unit_stat_data[:3]).strip()
        status = (unit_stat_data[4:7]).strip()
        if not status in ['ON','OFF']:
            logger.warning('param unit_stat_data %s error, ignored.' % unit_stat_data)
            return False
        sett = (unit_stat_data[8:11]).strip()
        roomt = (unit_stat_data[12:18]).strip()
        fanspeed = (unit_stat_data[19:23]).strip()
        opmode = (unit_stat_data[24:28]).strip()
        ecode = (unit_stat_data[29:]).strip() 
        if ecode != 'OK':
            logger.warning('param unit_stat_data %s error, ignored.' % unit_stat_data)
            return False   
        unitStat,created = CMUnitStat.objects.get_or_create(uid = uid)
        if created:
            unitStat.status = status
            unitStat.sett = sett
            unitStat.roomt = roomt
            unitStat.fanspeed = fanspeed
            unitStat.opmode = opmode
            unitStat.ecode = ecode
            unitStat.save()
            logger.info('new unit %s stat entry created' % uid)
            return True
        else:
            if (unitStat.status != status) or \
                    (unitStat.sett != sett) or \
                    (unitStat.roomt != roomt) or \
                    (unitStat.fanspeed != fanspeed) or \
                    (unitStat.opmode != opmode) or \
                    (unitStat.ecode != ecode):
                logger.info('unit %s previous stat: %s' % (uid,
                                                str(unitStat)))
                unitStat.status = status
                unitStat.sett = sett
                unitStat.roomt = roomt
                unitStat.fanspeed = fanspeed
                unitStat.opmode = opmode
                unitStat.ecode = ecode
                unitStat.save()
                logger.info('unit %s new stat %s' % (unitStat.uid, str(unitStat)))
                return True
            else:
                return False
    
    def __str__(self):
        return str([self.uid,self.status,self.sett,self.roomt,self.fanspeed,self.opmode,self.ecode])

    
