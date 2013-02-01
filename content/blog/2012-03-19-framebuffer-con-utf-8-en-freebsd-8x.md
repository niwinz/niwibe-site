Title: Framebuffer con UTF-8 en FreeBSD >= 8.x
Tags: freebsd, unicode

Leyendo varias noticias me he encontrado con un articulo que explica (en ruso) como poder tener "framebuffer" con caracteres unicode en la consola de FreeBSD.

Esta mejora se ha introducido en la rama 8, por lo que para usarlo tendríamos que tener la actual 8.2 o 9.0.

El sistema grafico "framebuffer" fue introducido hace 13 años (version 3.0). Para activarlo compilamos el nucleo con las siguientes opciones:

    options SC_PIXEL_MODE
    options VESA

### Ver los modos de vídeo disponible y activamos uno: ###

Una vez compilado el kernel y haber reiniciado, inicie sesión con el usuario root y teclee el siguiente comando:

    vidcontrol -i mode

Vera una larga lista de modos disponibles, en este ejemplo seleccionamos el de "1024x768" y que en mi caso esta resolución es el modo 280. Para activarlo, ejecutamos el siguiente comando:

    vidcontrol MODE_280

Si esto ha funcionado, bien. En caso contrario si ve una pantalla en blanco, quiere decir que su tarjeta de vídeo o el monitor no tiene soporte para este modo. Tendrá que ir a otra terminal y probar otro modo.

Una vez sabemos, que modo es el que nos funciona, lo dejamos por defecto con la siguiente opcion en «/etc/rc.conf»:

    allscreens_flags="MODE_280"


### Soporte UTF-8 en syscons: ###

Nota: esto no lo he probado personalmente por lo que no puedo asegurar que funcione tal cual. Los datos los he sacodo del siguiente articulo: <http://dadv.livejournal.com/162099.html>. En cuanto confirme, borrare esta nota.

FreeBSD 8.x como las versiones anteriores utilizan «cons25» como tipo de consola por defecto. Para activar utf-8, tenemos que cambiarnos a «xterm». En FreeBSD 9, xterm ya es la opción por defecto.

Añadimos las siguientes opciones a la configuración del kernel:

    options         TEKEN_XTERM             # xterm-style terminal emulation (Only on freebsd <= 8.x)
    options         TEKEN_UTF8              # UTF-8 output handling


Segun el articulo, para que los cambios funcionen de manera permanente hay que modificar «/boot/device.hints» y añadir 0x80 a los flags de syscons (anteriormente el valor era 0x100):

    hint.sc.0.flags="0x180"

Instalamos «sysutils/jfbterm» de los ports, es el terminal que se encargaría de pintar los caracteres en modo de vídeo. Ademas debemos modificar «/etc/ttys» y cambiar «cons25» por «xterm» en caso de estar en FreeBSD < 9.x.

Seteamos la variable de entorno LANG por ejemplo con "ru_RU.UTF-8" mediante los clases de inicio de sesión (login class) o mediante la configuración de la shell por defecto. Entramos y comprobamos que realmente esta variable esta asignada tal como deseamos y ejecutamos jfbterm, es posible que con este comando nuestro modo de vídeo cambie.

Para comprobar el modo de vide actual existen varias formas:

    vidcontrol -i adapter < /dev/ttyv0
    vidcontrol -i mode < /dev/ttyv0

Sin jfbterm los caracteres cirilicos no podrían pintarse adecuadamente.
