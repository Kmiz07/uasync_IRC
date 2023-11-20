# uasync_IRC
libreria asyncronica para conexion a irc
Se conecta a un servidor irc y procesa mensajes y usuarios en el canal.
hay que proporcionar canal, password de canal,nick,servidor, puerto y una funcion a la que acudir cuando hay alguna novedad.
se recibira *>>>lista de usuarios al entrar al canal; +>>>usuario cuando entra un usuario nuevo al canal; ->>>usuario cuando se desconecta del canal y usuario>>>mensaje al recibir algun mensaje desde el canal.
se puede enviar mensajes al canal mediante la funcion [irc_async.enviar_mensaje(mensaje)|]
Proporciona comunicacion en un canal con password.
precisa estar conectado a una red wifi.
