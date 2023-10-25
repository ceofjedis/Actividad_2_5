import network
import socket
import time
from machine import Pin

# Configuración del LED y Wi-Fi
led = Pin("LED", Pin.OUT)
ssid = 'INFINITUM0C54_2.4'
password = 'tDhavstaJX'

# Configuración de red Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Esperar a conectarse o fallar
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('Esperando conexión...')
    time.sleep(1)

# Manejar errores de conexión
if wlan.status() != 3:
    raise RuntimeError('Error en la conexión de red')
else:
    print('Conectado')
    status = wlan.ifconfig()
    print('Dirección IP:', status[0])

# Configuración del servidor web
html = """<!DOCTYPE html>
<html>
<head> <title>Pico W</title> </head>
<body> <h1>Pico W</h1>
<p>%s</p>
</body>
</html>
"""

# Abrir socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Escuchando en', addr)

# Escuchar conexiones
while True:
    try:
        cl, addr = s.accept()
        print('Cliente conectado desde', addr)
        request = cl.recv(1024).decode('utf-8')
        print(request)

        led_on = '/light/on' in request
        led_off = '/light/off' in request

        if led_on:
            print("Encender LED")
            led.on()
            state = "LED encendido"
        elif led_off:
            print("Apagar LED")
            led.off()
            state = "LED apagado"
        else:
            state = "Estado desconocido"

        response = html % state

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response.encode('utf-8'))
        cl.close()

    except OSError as e:
        cl.close()
        print('Conexión cerrada')

