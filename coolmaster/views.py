#from django.shortcuts import render
from django.http import HttpResponse
import serial, logging, json

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
    
    cmd_exec = cmd + ' ' + arg + '\r\n'
    instr = get_coolmaster_instrument()
    instr.open()
    instr.write(cmd_exec)
    cmd_result = instr.readlines()
    instr.close()
    
    response = HttpResponse(content_type='text/plain')
    
    response.content = 'command execute: ' + cmd_exec + '\n' + cmd_result

    return response
