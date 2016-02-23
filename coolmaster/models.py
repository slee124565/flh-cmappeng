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

class CoolMaster():
    """
    Instrument class for CoolMaster process controller.
    
    Communicates via RS232 Serial port, using the `serial` 
    Python module.
    
    This driver is intended to enable control of the CoolMaster 
    controller from the command line.
    """
    def __init__(self, serial_port, 
                        baudrate = 9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 0.5):
        
        instr = serial.Serial(port = serial_port,
                              baudrate = baudrate,
                              parity = parity,
                              stopbits = stopbits,
                              bytesize = bytesize,
                              timeout = timeout)
        return instr
    
