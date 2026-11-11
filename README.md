# Avellaneda a un Toque – Automatizador de publicaciones

Script en Python que usa **Selenium** para cargar productos de forma automática en el panel de administración de [Avellaneda a un Toque](https://admin.avellanedaauntoque.com), a partir de una planilla CSV.

En lugar de completar el formulario a mano producto por producto, se prepara un CSV y el script se encarga de:

1. Iniciar sesión con tu cuenta.
2. Borrar las publicaciones existentes.
3. Completar el formulario de cada producto (título, categoría, precios, compra mínima, talles y descripción).
4. Subir las imágenes y publicar.
5. Mostrar un resumen final con los productos subidos y los que dieron error.

> ⚠️ **Atención:** por defecto el script **borra TODAS las publicaciones de la cuenta** antes de subir las nuevas. Si no querés eso, usá la opción `--conservar-existentes`.

> Proyecto personal para uso con tu propia cuenta. No está afiliado a Avellaneda a un Toque. Si la web cambia su diseño, algunos selectores pueden dejar de funcionar.

## Tecnologías

- Python 3.10+
- Selenium 4
- python-dotenv

## Instalación

1. Cloná el repositorio y entrá en la carpeta:
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd TU_REPOSITORIO
   ```
2. (Recomendado) Creá un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Linux / macOS
   ```
3. Instalá las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Necesitás tener **Google Chrome** instalado (Selenium descarga el driver automáticamente).

## Configuración

Copiá `.env.example` como `.env` y completalo con tus datos:

```env
AAUT_USER=tu_email@ejemplo.com
AAUT_PASSWORD=tu_contraseña
AAUT_CSV=productos.csv
AAUT_TIEMPO_ESPERA=20
AAUT_RECARGO_MINORISTA=3000
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `AAUT_USER` | Sí | Email de tu cuenta |
| `AAUT_PASSWORD` | Sí | Contraseña de tu cuenta |
| `AAUT_CSV` | No | Ruta al CSV (por defecto `productos.csv`) |
| `AAUT_TIEMPO_ESPERA` | No | Segundos máximos de espera por elemento (por defecto 20) |
| `AAUT_RECARGO_MINORISTA` | No | Monto que se suma al precio mayorista para calcular el minorista (por defecto 3000) |

El archivo `.env` está en `.gitignore`: **nunca se sube al repositorio**.

## Formato del CSV

El archivo usa `;` como separador y debe tener estas columnas:

| Columna | Descripción |
|---|---|
| `subir` | `si` para subir el producto (cualquier otro valor lo omite) |
| `titulo` | Nombre del producto |
| `categoria` | Texto exacto de la categoría, como aparece en la web |
| `precio_mayorista` | Precio mayorista (acepta formatos como `$12.500,00`) |
| `compra_minima` | Cantidad mínima de compra |
| `talles` | Valor a cargar en el campo de talles |
| `descripcion` | Descripción del producto |
| `ruta_imagen` | Ruta de una o más imágenes, separadas por `\|` |

Hay un ejemplo en [`productos_ejemplo.csv`](productos_ejemplo.csv).

## Uso

```bash
python main.py                          # borra todas las publicaciones y sube las del CSV
python main.py --conservar-existentes   # sube las del CSV sin borrar nada
```

Al terminar, el script muestra un resumen con los productos publicados y los errores. Si un producto falla (por ejemplo, una imagen que no existe), se registra y continúa con el siguiente.

## Estructura del proyecto

```
.
├── main.py                 # Flujo principal y automatización con Selenium
├── config.py               # Lectura de configuración desde .env
├── requirements.txt        # Dependencias
├── productos_ejemplo.csv   # CSV de ejemplo con datos ficticios
├── .env.example            # Plantilla de configuración
└── .gitignore
```

## Posibles mejoras

- Dividir el código en módulos (navegador, CSV, páginas de la web).
- Reemplazar los `print` por el módulo `logging` con archivo de registro.
- Guardar el progreso para poder retomar si el script se corta a mitad de camino.
- Modo `--dry-run` para validar el CSV sin publicar.
- Tests automáticos para el procesamiento del CSV y de los precios.
