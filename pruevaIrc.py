import uasyncio
import irc_asyncV2
from machine import Pin
led=Pin(2,Pin.OUT)
led.value(1)
async def evento(origen,mensaje):
    global led
    print(f'{origen}>>>{mensaje}')
    if mensaje =='ledON':led.value(0)
    if mensaje =='ledOFF':led.value(1)

async def bucle_programa():
    estado_flash=1
    flash=Pin(0,Pin.IN)
    irc= irc_asyncV2.irc_conexion(evento,"irc.dal.net",6667,'espnmcu9','#canal','micropython','uno','dos','tres','cuatro')
    uasyncio.create_task(irc.conectar())
    while True:
        await uasyncio.sleep(0)
        if flash.value() != estado_flash:
            await irc.envia_mensaje(f'Flash{flash.value()}')
            estado_flash=flash.value()
uasyncio.run(bucle_programa())