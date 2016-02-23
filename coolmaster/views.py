#from django.shortcuts import render
from django.http import HttpResponse
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
        nbyte = instr.write(cmd_exec.encode())
        logger.debug('write command [%s] and %d bytes sent.' % (cmd_exec,nbyte))
        time.sleep(0.5)
        rtn_data = b''
        while instr.inWaiting():
            rtn_data += instr.read(1024)
        #cmd_result_lines = instr.readlines()
        logger.debug('get response data : %s' % rtn_data.decode())

        resp_data = 'command execute: ' + cmd_exec + '\n' + rtn_data.decode()
    except:
        logger.error('Serial Port Exception!', exc_info=True)
        resp_data = 'CMStation Internal ERROR'
        
    instr.close()
    
    response = HttpResponse(content_type='text/plain')
    

    response.content = resp_data
    return response
