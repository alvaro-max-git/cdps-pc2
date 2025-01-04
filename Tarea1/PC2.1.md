# Script preparación escenario

### Basarnos en el de la PC1
Automatiza la creación de la máquina virtual.

#### Creamos carpeta
```bash
/mnt/tmp/alvaro.pablo
```

#### Copiamos base
```bash
/lab/cdps/p2/cdps-vm-base-p2.qcow2
```

#### Copiamos xml desde carpeta personal a `alvaro.pablo`
*(ver cambios en prueba manual).*

#### Creamos la imagen
```bash
qemu-img create -F qcow2 -f qcow2 -b cdps-vm-base-p2.qcow2 PC2.qcow2
```

---

# Arranque máquina virtual

### Basarnos en el de la PC1
```bash
sudo virsh undefine PC2  # Por si acaso
sudo virsh define PC2.xml
sudo virsh start PC2
```

Abrir consola *(como la PC1, en otra ventana)*.

> **Nota:** Podemos tener funciones para `stop/destroy`.

---

### Idea/Opcional: Arranque instalación automático
Para ejecutar scripts al arrancar la máquina virtual podríamos usar:
```bash
/etc/rc.local
```

---

# Instalación App

En principio no actualizamos el sistema *(tarda mucho).*

### Instalamos pip
```bash
sudo apt-get python3-pip
```
> **Nota:** `git` y `python3` están ya instalados en la MV.

### Actualizamos `json2html`, si no da error:
```bash
pip3 install --upgrade json2html
```
> Ver si podemos agregarlo a la lista de `requirements.txt`.

---

### Clonar repositorio
```bash
git clone https://github.com/CDPS-ETSIT/practica_creativa2.git
cd practica_creativa2/bookinfo/src/productpage
```

> **Nota:** Se puede cambiar el directorio de trabajo en Python:
```python
os.chdir('../')
os.chdir(r"C:\Users\Gfg\Desktop\geeks")
```

---

### Editar `requirements.txt` e instalar dependencias

1. Editar el archivo `requirements.txt`:
   - Elimina la versión del paquete `requests`. Deja la línea como:
     ```
     requests
     ```
   - Intentar agregar `upgrade json2html`.
2. Instalar dependencias:
   ```bash
   pip3 install -r requirements.txt
   ```

---

### Probar la app
1. Miramos nuestra IP:
   ```bash
   ip addr  # o ipconfig en Windows
   ```
2. Ejecutamos:
   ```bash
   python3 productpage_monolith.py 8080
   ```

Podemos entrar desde el host en:
```
<IP>:8080
```

---

# Cambiar el título de la página

1. En `templates/index.html` y `templates/productpage.html` sustituimos:
   ```html
   {% block title %}Simple Bookstore App{% endblock %}
   ```
   por:
   ```html
   {% block title %}Grupo {{ grup_num }}{% endblock %}
   ```

2. Ahora definimos `grup_num` en `productpage_monolith.py`:
   ```python
   import os  # Asegúrate de que ya está importado

   # Leer la variable de entorno GRUP_NUM
   grup_num = os.getenv("GRUP_NUM", "Default Group")  # Valor por defecto "Default Group"

   # Habilitar recarga automática de plantillas
   # DESPUES de definir app, si no da error
   app.config['TEMPLATES_AUTO_RELOAD'] = True
   ```

3. También añadimos la variable en los renders:
   - **Línea 245:** `index()`:
     ```python
     return render_template('index.html', serviceTable=table, grup_num=grup_num)
     ```
   - **Línea 309:** `front()`:
     ```python
     return render_template(
         'productpage.html',
         detailsStatus=detailsStatus,
         reviewsStatus=200,
         product=product,
         details=details,
         reviews={"R1": "OK"},
         user=user,
         grup_num=grup_num
     )
     ```

4. En la consola ejecutamos **antes de ejecutar la app**:
   ```bash
   export GRUP_NUM="39"
   ```

---

# Cambiar el puerto de arranque

Para cambiar el puerto por defecto:
```python
p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
app.run(host='0.0.0.0', port=p, debug=True, threaded=True)
```
```