#from django.shortcuts import render
from django.http import HttpResponse
from serial import SerialException
import serial, logging, json, time
import binascii

from coolmaster.models import get_coolmaster_instrument

logger = logging.getLogger(__name__)
# Create your views here.

def bytecmd_api(request):
    """
    Trigger CoolMaster to write byte array to RS232 serial port. 
    
    Handle HTTP Get request with hex string argument from network 
    and trigger CoolMaster to covert hex string to byte array and
    write to RS232 serial port. And convert response data to hex
    string as HTTP Respose content.
    The HTTP GET URL example:: 
    
        http://url_request_path/?arg=1a2c3d4b
    
    Parameters:
    
    - `arg`: the CoolMaster command argument value in querystring. 
    """
    hexstring = request.GET.get('arg')
    logger.info('http request coolmaster execute byte command with arg $s' % hexstring)
    bdata = binascii.unhexlify(hexstring)

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
            nbyte = instr.write(bdata)
            instr.flush()
            logger.debug('byte command write')
            time.sleep(1)
            
            rtn_data = b''
            rtn_byte = instr.read()
            rtn_hex = binascii.b2a_hex(rtn_byte)
            logger.debug('get response data hex : \n%s' % rtn_hex)

            if len(rtn_byte) == 0:
                logger.warning('no data received from serial connection!')
                instr.close()
                time.sleep(0.5)
                logger.warning('retry %d time' % ncount)
                ncount += 1
            else:
                break

        if len(rtn_byte) == 0:
            logger.error('no response data for byte command')
            resp_data = 'ERROR: No Data from Serial Port'
        else:
            resp_data = rtn_hex
    except:
        logger.error('Serial Port Exception!', exc_info=True)
        resp_data = 'CMStation Internal ERROR'
            
        instr.close()
    
    response = HttpResponse(content_type='text/plain')
    

    response.content = resp_data
    return response


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
        instr.open()
        nbyte = instr.write(cmd_exec.encode())
        logger.debug('write command [%s] and %d bytes sent.' 
                            % (cmd_exec.replace('\r\n','\\r\\n'),nbyte))
        
        if cmd == 'stat':
            logger.debug('enter stat check process')
            lines = instr.readlines()
            logger.debug('readlines count %d' % len(lines))
            rtn_data = b''
            for line in lines:
                rtn_data += line
            logger.debug('get response data : \n%s' % rtn_data.decode())
            
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
                logger.debug('rtn data hex:\n%s' % rtn_hex)
                resp_data = rtn_data.decode().strip()
                logger.debug('rtn data string:\n%s' % resp_data)
                
                #-> return last stat result
                pos = resp_data.rfind('stat')
                if pos >= 0:
                    resp_data = resp_data[pos:]
                    logger.debug('stat result return:\n%s' % resp_data)
                    
        else:
            if nbyte > 0:
                resp_data = 'Command Write OK'
            else:
                resp_data = 'Command Write Fail'
                logger.error('command [%s] write fail' % cmd_exec.replace('\r\n','\\r\\n'))
                
    except:
        logger.error('Serial Port Exception!', exc_info=True)
        resp_data = 'CMStation Internal ERROR'
    
    finally:        
        instr.close()
        response = HttpResponse(content_type='text/plain')
        response.content = resp_data
        return response

def hc2_vd_update_simulation(request):
    logger.info('hc2_vd_update_simulation triggered')
    return HttpResponse('Simulation Response OK')

