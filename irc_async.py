import uasyncio
import usocket,ure
terminar=False
canal=''
password=''
usuarios=[]
cliente_irc=None
evento=None
async def inicia_conexion(event,host,puerto,nick,chan,passw):
    global canal
    global password
    global cliente_irc
    global evento
    canal=chan
    password=passw
    evento=event
    cliente_irc=usocket.socket()
    irc_host=usocket.getaddrinfo(host,puerto)[0][-1]
    cliente_irc.connect(irc_host)
    cliente_irc.setblocking(False)
    cliente_irc.send(f"NICK {nick}\n")
    cliente_irc.send("USER uno dos tres : ESP IOT\n")
    uasyncio.create_task(recibe(cliente_irc))
#     return cliente_irc
    while not terminar:
        await uasyncio.sleep(0)

async def recibe(cliente_irc):
#     print(cliente_irc)
    bufer=[]
    global terminar
    while not terminar:
        while True:
            try:
                linea=cliente_irc.readline()
                if linea:
                    bufer.append(linea)
                else:
                    break
            except:
                pass
        if len(bufer)>0:
            await procesa_linea(cliente_irc,bufer.pop(0))
        await uasyncio.sleep(0)
async def enviar_mensaje(mensaje):
    global cliente_irc
    cliente_irc.send(f'PRIVMSG #nmcuesp :{mensaje}\r\n')
    
async def procesa_linea(cliente_irc,linea):
    global canal
    global password
    global usuarios
    global evento
#     print(linea)
    if linea.decode().find('PING')==0:# caso PING
        palabras=linea.decode().split(' ')
        cliente_irc.send('PONG '+palabras[1]+'\r\n')
#         print('PONG '+palabras[1])
    else:
        muestra=linea.decode().split(' ')
        if len(muestra) >3:
            origen=muestra[0]
            comando=muestra[1]
            destino=muestra[2]
            resto=' '.join(muestra[3:])
#             print(f"Origen: {origen}\nComando:{comando}\nDestino:{destino}\nResto={resto}\n")
            if comando=='376':#fin de mensaje inicial¿abrir canal?
                cliente_irc.send(f'JOIN {canal}\r\n')
            if comando=='366':#canal abierto, ¿pongo pass canal?
                cliente_irc.send(f'MODE {canal} +k {password}\r\n')
            if comando=="PRIVMSG":
                origen_privmsg=ure.match(':(\w+)!',origen).group(1)
                mensaje_privmsg=resto[1:]
                await evento(origen_privmsg,mensaje_privmsg)
#                 print(f'origen_privmsg={origen_privmsg} ; destino= {destino} ; mensaje_privmsg= {mensaje_privmsg} ')
            if comando=='PART'or comando=='QUIT':#Comando PART o QUIT User sale del canal, tambien si salgo yo.
                if destino==canal:
                    usuarios.remove(ure.match(':(\w+)!',origen).group(1))
                    await evento('-',ure.match(':(\w+)!',muestra[0]).group(1))
#                     print(usuarios)
            if comando == '475':#comando 475 password erroneo entrando en canal. Normalmente el canal esta ocupado
                cliente_irc.send(f'JOIN {canal} {password}\r\n')
            if comando == '353':
#                 await evento('*',resto[len(canal)+4:-2])
                usuarios=resto[len(canal)+4:-2].split(' ')
                await evento('*',usuarios)
                
        elif len(muestra)==3:
            if muestra[1]=='JOIN':#comando JOIN nuevo user en canal, incluso cuando entre el esp.
                if ure.match(':(#\w+)\r\n',muestra[2]).group(1)==canal:
                    usuarios.append(ure.match(':(\w+)!',muestra[0]).group(1))
                    await evento('+',ure.match(':(\w+)!',muestra[0]).group(1))
            

#                 print(usuarios)
            #comando 482 se quiso poner pass a un canal sin ser oper
            #comando 353 lista de users en canal, si es diferente de solo mi nick es que el canal ya estaba ocupado. habria que salir y cambiar de canal
            #Comando=MODE confirma un estado de canal o usuario


