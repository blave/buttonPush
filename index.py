import time
import RPi.GPIO as GPIO
import urllib2

from iofog_container_sdk.client import IoFogClient, IoFogException
from iofog_container_sdk.iomessage import IoMessage
from iofog_container_sdk.listener import *

current_config = None
client = IoFogClient()

DELAY = 2.0
LATCH_DURATION = 0.05
IP_ADDRESS = 'http://192.168.0.100:16000'

gpioInput1 = 18
gpioOutput1 = 23

GPIO.setmode( GPIO.BCM )

GPIO.setup( gpioInput1, GPIO.IN, pull_up_down = GPIO.PUD_UP )
GPIO.setup( gpioOutput1, GPIO.OUT )

def update_config():
    attempt_limit = 5
    config = None

    while attempt_limit > 0:
        try:
            config = client.get_config()
            print 'attempt_limit = {}'.format( attempt_limit )
            break
        except IoFogException, ex:
            attempt_limit -= 1
            print str(ex)

    if attempt_limit == 0:
        print 'Config update failed :('
        return

    global current_config
    current_config = config

def detectButtonPush():
    input_state = GPIO.input( gpioInput1 )
    if input_state == False:
        config = current_config
        print 'config = {}'.format(config)
        print( "Button Pressed" )
        GPIO.output( gpioOutput1, True )
        time.sleep( config.get( 'latchduration', LATCH_DURATION ) )
        print 'latchduration = {}'.format( LATCH_DURATION )
        GPIO.output( gpioOutput1, False )

        
        try:
            content = urllib2.urlopen( config.get('ipaddress', IP_ADDRESS ), timeout = 1 ) 
        except urllib2.URLError, e:
            print type(e)
       
        time.sleep( config.get ('delay', DELAY ) )

class ControlListener(IoFogControlWsListener):
    def on_control_signal(self):
        update_config()


class MessageListener(IoFogMessageWsListener):
    def on_receipt(self, message_id, timestamp):
        print 'Receipt: {} {}'.format(message_id, timestamp)


update_config()
client.establish_message_ws_connection(MessageListener())
client.establish_control_ws_connection(ControlListener())

while True:
    detectButtonPush()
