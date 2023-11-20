import irc_async,uasyncio

async def evento(origen,mensaje):
    print(f'{origen}>>>{mensaje}')
    
    
    
    
    
async def ciclo():
    uasyncio.create_task(irc_async.inicia_conexion(evento,"irc.freenode.org",6667,'uPython','#nmcuesp','micropython'))
    while True :
        #aqui el codigo ciclico de programa
        await uasyncio.sleep(0)

uasyncio.run(ciclo())
                         
                         
                         
