import uasyncio,usocket,ure

class irc_conexion:
    def __init__(self,eventos,ip,puerto,nick,canal,passw,ident1,ident2,ident3,ident4):
        self.eventos=eventos
        self.ip=ip
        self.puerto=puerto
        self.nick=nick
        self.canal=canal
        self.passw=passw
        self.ident1=ident1
        self.ident2=ident2
        self.ident3=ident3
        self.ident4=ident4
        self.usuarios=[]
        
    async def conectar(self):
        addr=usocket.getaddrinfo(self.ip,self.puerto)[0][-1]
        self.reader,self.writer=await uasyncio.open_connection(addr[0],addr[1])
        await uasyncio.sleep_ms(100)
        self.writer.write(f"NICK {self.nick}\n".encode())
        self.writer.write(f"USER {self.ident1} {self.ident2} {self.ident3} : {self.ident4}\n".encode())
        await self.writer.drain()
        while True:
            linea = await self.reader.readline()
            if linea != b'': await self.procesa_linea(linea)
            uasyncio.sleep(0)
            
    async def procesa_linea(self, linea):
        print(linea.decode())
        if linea.decode().find('PING')==0:# caso PING
            palabras=linea.decode().split(' ')
            await self.envia(f'PONG {palabras[1]}\r\n')
            print(f'PONG {palabras[1]}')
            
        else:
            muestra=linea.decode().split(' ')
            if len(muestra) >3:
                origen=muestra[0]
                comando=muestra[1]
                destino=muestra[2]
                resto=' '.join(muestra[3:])
                if comando=='376':#fin de mensaje inicial¿abrir canal?
                    await self.envia(f'JOIN {self.canal}\r\n')
                if comando=='366':#canal abierto, ¿pongo pass canal?
                    await self.envia(f'MODE {self.canal} +k {self.passw}\r\n')
                if comando=="PRIVMSG":
                    origen_privmsg=ure.match(':(\w+)!',origen).group(1)
                    mensaje_privmsg=resto[1:].replace('\r\n','')#se eliminan ':'en el inic io y '\r\n'en el final de la linea
                    uasyncio.create_task(self.eventos(origen_privmsg,mensaje_privmsg))
                if comando=='PART'or comando=='QUIT':#Comando PART o QUIT User sale del canal, tambien si salgo yo.
                    if destino==self.canal:
                        self.usuarios.remove(ure.match(':(\w+)!',origen).group(1))
                        await self.eventos('SALE',ure.match(':(\w+)!',muestra[0]).group(1))
                if comando == '475':#comando 475 password erroneo entrando en canal. Normalmente el canal esta ocupado
                    await self.envia(f'JOIN {self.canal} {self.passw}\r\n')
                if comando == '353':
                    self.usuarios=resto[len(self.canal)+4:-2].split(' ')
                    uasyncio.create_task(self.eventos('*',self.usuarios[:-1]))
            elif len(muestra)==3:
                if muestra[1]=='JOIN':#comando JOIN nuevo user en canal, incluso cuando entre el esp.
                    if ure.match(':?(#\w+)\r\n',muestra[2]).group(1)==self.canal:
                        self.usuarios.append(ure.match(':(\w+)!',muestra[0]).group(1))
                        uasyncio.create_task(self.eventos('ENTRA',ure.match(':(\w+)!',muestra[0]).group(1)))
                
    async def envia(self,linea):
        self.writer.write(linea.encode())
        await self.writer.drain()
        
    async def envia_mensaje(self,mensaje):
        await self.envia(f"PRIVMSG {self.canal} :{mensaje}\r\n")
        
    

