#from django.shortcuts import render
from django.http import HttpResponse
from serial import SerialException
import serial, logging, json, time

from coolmaster.models import get_coolmaster_instrument

logger = logging.getLogger(__name__)
# Create your views here.

def cm_api(request,cmd):
    """
    Trigger CoolMaster to execute `cmd` command. Return CoolMaster 
    response directly.
    
    Handle HTTP Get request from network and trigger CoolMaster
    through RS232 serial port to execute the `cmd` command. 
    If the `cmd` need argument vaule, it should be passed by
    querystring with variable name *arg*. For example,
    http://url_request_path/<cmd>/?arg=<arg_value>
    
    Parameters:
    
    - `cmd`: the command name needs CoolMaster to execute.
    - `arg`: the CoolMaster command argument value in querystring. 
    """
    arg = request.GET.get('arg')
    logger.info('http request coolmaster execute command %s with arg %s' % (cmd,arg))
    
    if arg is None:
        cmd_exec = cmd + '\r\n'
    else:
        cmd_exec = cmd + ' ' + arg + '\r\n'

    try:
        instr = get_coolmaster_instrument()
        ncount = 1
        while ncount < 5:
            if instr.isOpen() == False:
                logger.debug('opening serial port %s' % instr.port)
                try:
                    instr.open()
                except SerialException:
                    logger.warning('serial port is already in used.')
                    rtn_data = b'ERROR: Serial Port In Used'
                    break
            nbyte = instr.write(cmd_exec.encode())
            instr.flush()
            logger.debug('write command [%s] and %d bytes sent.' 
                                % (cmd_exec.replace('\r\n','\\r\\n'),nbyte))
            time.sleep(1)
            
            rtn_data = b''
            lines = instr.readlines()
            logger.debug('readlines count %d' % len(lines))

            logger.debug('is data remain %d' % instr.inWaiting())

            for line in lines:
                rtn_data += line
            logger.debug('get response data : \n%s' % rtn_data.decode())

            if len(rtn_data) == 0:
                logger.warning('no data received from serial connection!')
                instr.close()
                time.sleep(0.5)
                logger.warning('retry %d time' % ncount)
                ncount += 1
            else:
                break

        if len(rtn_data) == 0:
            logger.error('no response data for command [%s]' % cmd_exec.replace('\r\n','\\r\\n'))
            resp_data = 'ERROR: No Data from Serial Port'
        else:
            if len(rtn_data) > 0 and rtn_data[0] == 0:
                logger.warning('receive byte array exist 0x00 at the begining, remove head 0x00 byte')
                rtn_data = rtn_data[1:]
            if len(rtn_data) > 0 and rtn_data[-1] == 0:
                logger.warning('reveive byte array exist 0x00 at the end, removed endj 0x00 byte')
                rtn_data = rtn_data[:-1]

            rtn_hex = ''
            for i in range(len(rtn_data)):
                rtn_hex += hex(rtn_data[i]) + ' '
            logger.debug('rtn data hex: %s' % rtn_hex)
            resp_data = 'command execute: ' + cmd_exec + '\n' + rtn_data.decode().strip()
    except:
        logger.error('Serial Port Exception!', exc_info=True)
        resp_data = 'CMStation Internal ERROR'
            
        instr.close()
    
    response = HttpResponse(content_type='text/plain')
    

    response.content = resp_data
    return response

def hc2_vd_update_simulation(request):
    logger.info('hc2_vd_update_simulation triggered')