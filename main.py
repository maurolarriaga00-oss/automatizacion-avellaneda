import argparse
import csv
import os
import time
import traceback
import random

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import (
    WebDriverWait,
    Select
)

from selenium.webdriver.support import expected_conditions as EC

from config import (
    URL,
    USUARIO,
    PASSWORD,
    CSV_PRODUCTOS,
    TIEMPO_ESPERA,
    RECARGO_MINORISTA
)

# ======================================================
# ESTADO GLOBAL
# ======================================================

driver = None

# Columnas que tiene que tener el CSV para que el script funcione
COLUMNAS_REQUERIDAS = [
    "subir",
    "titulo",
    "categoria",
    "precio_mayorista",
    "compra_minima",
    "talles",
    "descripcion",
    "ruta_imagen",
]

publicaciones_ok = []
publicaciones_error = []

# ======================================================
# LOGS
# ======================================================

def titulo(texto):

    print("\n" + "="*70)
    print(texto)
    print("="*70)


def ok(texto):
    print(f"✅ {texto}")


def error(texto):
    print(f"❌ {texto}")


def aviso(texto):
    print(f"⚠ {texto}")

# ======================================================
# PAUSA HUMANA
# ======================================================

def pausa_humana(inicio, minimo=30, maximo=45):

    tiempo_transcurrido = time.time() - inicio

    tiempo_objetivo = random.uniform(minimo, maximo)

    if tiempo_transcurrido < tiempo_objetivo:

        espera = tiempo_objetivo - tiempo_transcurrido

        ok(f"Pausa humana: {espera:.1f} segundos")

        time.sleep(espera)

    else:

        ok("No hace falta pausa.")

# ======================================================
# NAVEGADOR
# ======================================================

def iniciar_navegador():

    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors")

    # Selenium 4.6+ descarga el driver correcto automáticamente
    navegador = webdriver.Chrome(options=options)

    return navegador

# ======================================================
# ESPERAS
# ======================================================

def esperar(by, valor):

    return WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.presence_of_element_located((by, valor))
    )


def esperar_click(by, valor):

    return WebDriverWait(driver, TIEMPO_ESPERA).until(
        EC.element_to_be_clickable((by, valor))
    )

# ======================================================
# VALIDAR IMÁGENES
# ======================================================

def validar_imagenes(lista):

    for imagen in lista:

        if not os.path.exists(imagen):

            error(f"No existe la imagen:\n{imagen}")

            return False

    return True

# ======================================================
# LEER CSV
# ======================================================

def cargar_publicaciones():

    publicaciones = []

    if not os.path.exists(CSV_PRODUCTOS):

        raise Exception("No existe el CSV.")

    with open(
        CSV_PRODUCTOS,
        encoding="utf-8"
    ) as archivo:

        lector = csv.DictReader(
            archivo,
            delimiter=";"
        )

        # Verificar que el CSV tenga todas las columnas necesarias
        faltantes = [
            c for c in COLUMNAS_REQUERIDAS
            if c not in (lector.fieldnames or [])
        ]

        if faltantes:

            raise Exception(
                "Al CSV le faltan estas columnas: "
                + ", ".join(faltantes)
            )

        for fila in lector:

            if fila.get("subir","").lower() != "si":
                continue

            # Las imágenes se separan con "|" (también se acepta ";")
            fila["ruta_imagen"] = [
                x.strip()
                for x in fila["ruta_imagen"].replace("|", ";").split(";")
                if x.strip()
            ]

            if not validar_imagenes(fila["ruta_imagen"]):

                publicaciones_error.append(
                    (
                        fila["titulo"],
                        "Imagen inexistente"
                    )
                )

                continue

            publicaciones.append(fila)

    return publicaciones

# ======================================================
# LOGIN
# ======================================================

def login():

    titulo("INICIANDO SESIÓN")

    driver.get(URL)

    usuario = esperar(By.NAME,"usuario")
    password = esperar(By.NAME,"password")

    usuario.clear()
    password.clear()

    usuario.send_keys(USUARIO)
    password.send_keys(PASSWORD)

    esperar_click(
        By.XPATH,
        "//button[contains(text(),'Iniciar Sesión')]"
    ).click()

    esperar_click(
        By.XPATH,
        "//p[contains(text(),'Ver mis publicaciones')]"
    )

    ok("Sesión iniciada correctamente.")

# ======================================================
# IR AL INICIO
# ======================================================

def volver_al_inicio():

    titulo("VOLVIENDO AL INICIO")

    esperar_click(
        By.CSS_SELECTOR,
        "button.MuiIconButton-root"
    ).click()

    esperar_click(
        By.XPATH,
        "//span[contains(text(),'Inicio')]"
    ).click()

    esperar_click(
        By.XPATH,
        "//p[contains(text(),'Publicar nuevo producto')]"
    )

    ok("Pantalla principal.")

# ======================================================
# ABRIR MIS PUBLICACIONES
# ======================================================

def abrir_publicaciones():

    titulo("ABRIENDO PUBLICACIONES")

    esperar_click(
        By.XPATH,
        "//p[contains(text(),'Ver mis publicaciones')]"
    ).click()

    ok("Listado abierto.")

# ======================================================
# MOSTRAR 100 PUBLICACIONES
# ======================================================

def mostrar_100():

    try:

        selector = esperar_click(
            By.XPATH,
            "//div[contains(text(),'10')]"
        )

        selector.click()

        esperar_click(
            By.XPATH,
            "//li[contains(text(),'100')]"
        ).click()

        ok("Mostrando 100 publicaciones.")

    except TimeoutException:

        aviso("No fue necesario cambiar el selector.")

# ======================================================
# CHECKBOXES
# ======================================================

def obtener_checkboxes():

    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);"
    )

    time.sleep(2)

    return driver.find_elements(
        By.XPATH,
        "//input[@type='checkbox']"
    )

# ======================================================
# SELECCIONAR PUBLICACIONES
# ======================================================

def seleccionar_publicaciones(checks):

    cantidad = len(checks)

    titulo(f"SELECCIONANDO {cantidad} PUBLICACIONES")

    for checkbox in checks:

        driver.execute_script(
            "arguments[0].scrollIntoView(true);",
            checkbox
        )

        driver.execute_script(
            "arguments[0].click();",
            checkbox
        )

    ok(f"{cantidad} publicaciones seleccionadas.")

    return cantidad

# ======================================================
# ELIMINAR PUBLICACIONES
# ======================================================

def eliminar_publicaciones():

    titulo("ELIMINANDO PUBLICACIONES")

    abrir_publicaciones()

    mostrar_100()

    checks = obtener_checkboxes()

    if len(checks) == 0:

        aviso("No existen publicaciones.")

        volver_al_inicio()

        return

    cantidad = seleccionar_publicaciones(checks)

    esperar_click(
        By.XPATH,
        "//button[contains(text(),'Borrar')]"
    ).click()

    esperar_click(
        By.XPATH,
        "//button[contains(text(),'Confirmar')]"
    ).click()

    ok(f"{cantidad} publicaciones eliminadas.")

    volver_al_inicio()

# ======================================================
# ABRIR FORMULARIO
# ======================================================

def abrir_formulario():

    titulo("ABRIENDO FORMULARIO")

    esperar_click(
        By.XPATH,
        "//p[contains(text(),'Publicar nuevo producto')]"
    ).click()

    esperar(
        By.NAME,
        "productName"
    )

    ok("Formulario abierto.")

# ======================================================
# COMPLETAR FORMULARIO
# ======================================================

def completar_formulario(publicacion):

    titulo(publicacion["titulo"])

    esperar(
        By.NAME,
        "productName"
    ).send_keys(
        publicacion["titulo"]
    )

    # --------------------------------------------------
    # CATEGORÍA
    # --------------------------------------------------

    categoria = Select(
        esperar(
            By.ID,
            "grouped-native-select"
        )
    )

    categoria.select_by_visible_text(
        publicacion["categoria"]
    )

    # --------------------------------------------------
    # PRECIO MAYORISTA
    # --------------------------------------------------

    precio_mayorista = float(
        publicacion["precio_mayorista"]
        .replace("$", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    esperar(
        By.NAME,
        "price"
    ).send_keys(
        str(int(precio_mayorista))
    )

    # --------------------------------------------------
    # PRECIO MINORISTA - OPCIONAL
    # Mayorista + RECARGO_MINORISTA (se configura en .env)
    # --------------------------------------------------

    precio_minorista = precio_mayorista + RECARGO_MINORISTA

    try:

        campo_minorista = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located(
                (By.NAME, "retailPrice")
            )
        )

        campo_minorista.clear()

        campo_minorista.send_keys(
            str(int(precio_minorista))
        )

        ok(
            f"Precio minorista cargado: "
            f"${int(precio_minorista)}"
        )

    except TimeoutException:

        aviso(
            "Precio minorista no disponible en esta cuenta. "
            "Continuando..."
        )

    # --------------------------------------------------
    # COMPRA MÍNIMA
    # --------------------------------------------------

    esperar(
        By.NAME,
        "minWholesale"
    ).send_keys(
        publicacion["compra_minima"]
    )

    # ======================================================
    # TALLE
    # ======================================================

    try:

        # Buscar específicamente el bloque "Talles"
        bloque_talles = esperar(
            By.XPATH,
            "//label[normalize-space()='Talles']/parent::div"
        )

        # Buscar el botón "Agregar" dentro de Talles
        boton_agregar = bloque_talles.find_element(
            By.XPATH,
            ".//button[normalize-space()='Agregar']"
        )

        boton_agregar.click()

        # Esperar el campo "Agregar valor..."
        campo_talle = WebDriverWait(
            driver,
            TIEMPO_ESPERA
        ).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//input[@placeholder='Agregar valor...']"
                )
            )
        )

        # Completar con el valor del CSV
        campo_talle.clear()

        campo_talle.send_keys(
            publicacion["talles"]
        )

        ok(
            f"Talle ingresado: {publicacion['talles']}"
        )

        # Esperar el botón Confirmar
        boton_confirmar = WebDriverWait(
            driver,
            TIEMPO_ESPERA
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[normalize-space()='Confirmar']"
                )
            )
        )

        boton_confirmar.click()

        ok("Talle confirmado.")

    except Exception as e:

        error(
            f"No se pudo completar el talle: {e}"
        )

        raise

    # --------------------------------------------------
    # DESCRIPCIÓN
    # --------------------------------------------------

    esperar(
        By.ID,
        "outlined-basic"
    ).send_keys(
        publicacion["descripcion"]
    )

    ok(
        f"Formulario completado. "
        f"Mayorista: ${int(precio_mayorista)} | "
        f"Minorista: ${int(precio_minorista)}"
    )

# ======================================================
# SUBIR IMÁGENES
# ======================================================

def subir_imagenes(driver, rutas_imagenes):

    titulo("SUBIENDO IMÁGENES")

    try:

        # ---------------------------------------------
        # Verificar que existan las imágenes
        # ---------------------------------------------

        for ruta in rutas_imagenes:

            if not os.path.exists(ruta):

                error(f"No existe la imagen:\n{ruta}")
                return False

        # ---------------------------------------------
        # Enviar imágenes
        # ---------------------------------------------

        input_file = esperar(
            By.CSS_SELECTOR,
            "input[type='file']"
        )

        input_file.send_keys("\n".join(rutas_imagenes))

        ok("Archivos enviados.")

        cantidad = len(rutas_imagenes)

        ok(f"Esperando carga de {cantidad} imagen(es)...")

        # ---------------------------------------------
        # Esperar hasta que aparezcan todas las imágenes
        # ---------------------------------------------

        ultimo = -1

        inicio = time.time()

        while True:

            imagenes = driver.find_elements(
                By.CSS_SELECTOR,
                "button[aria-label='delete']"
            )

            actuales = len(imagenes)

            if actuales != ultimo:

                print(f"   {actuales}/{cantidad}")

                ultimo = actuales

            if actuales >= cantidad:

                break

            if time.time() - inicio > 30:

                raise Exception(
                    "Tiempo agotado esperando imágenes."
                )

            time.sleep(0.2)

        ok("Todas las imágenes fueron cargadas.")

        # ---------------------------------------------
        # Dar un pequeño margen
        # ---------------------------------------------

        time.sleep(1)

        # ---------------------------------------------
        # Esperar que desaparezca el snackbar
        # ---------------------------------------------

        try:

            WebDriverWait(driver, 20).until(

                EC.invisibility_of_element_located(

                    (By.ID, "notistack-snackbar")

                )

            )

            ok("Snackbar finalizado.")

        except TimeoutException:

            aviso("No apareció snackbar.")

        # ---------------------------------------------
        # Esperar botón Publicar
        # ---------------------------------------------

        esperar_click(

            By.XPATH,

            "//button[contains(text(),'Publicar')]"

        )

        ok("Botón Publicar listo.")

        return True

    except Exception as e:

        error(f"Error subiendo imágenes: {e}")

        return False

# ======================================================
# PUBLICAR
# ======================================================

def publicar():

    esperar_click(
        By.XPATH,
        "//button[contains(text(),'Publicar')]"
    ).click()

    ok("Esperando publicación...")

    try:

        # Esperar que aparezca el cartel gris
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h5[contains(text(),'Publicando Producto')]")
            )
        )

        ok("Producto publicándose...")

        # Esperar que desaparezca
        WebDriverWait(driver, 180).until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//h5[contains(text(),'Publicando Producto')]")
            )
        )

    except TimeoutException:
        aviso("No se detectó el cartel de publicación.")

    ok("Publicación terminada.")

# ======================================================
# CERRAR POPUP
# ======================================================

def cerrar_popup():

    try:

        ok("Esperando popup...")

        # Esperar hasta 15 segundos a que aparezca
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(),'Lo tendré en cuenta')]")
            )
        )

        # Clic en "Lo tendré en cuenta"
        esperar_click(
            By.XPATH,
            "//button[contains(text(),'Lo tendré en cuenta')]"
        ).click()

        ok("Popup cerrado.")

    except TimeoutException:

        aviso("No apareció popup. Continuando...")

# ======================================================
# CERRAR FORMULARIO
# ======================================================

def cerrar_formulario():

    try:

        esperar_click(

            By.XPATH,

            "//button[@aria-label='close']"

        ).click()

        ok("Formulario cerrado.")

    except TimeoutException:

        try:

            esperar_click(

                By.XPATH,

                "//button[contains(text(),'Volver')]"

            ).click()

            ok("Formulario cerrado.")

        except TimeoutException:

            aviso("No fue posible cerrar el formulario.")

# ======================================================
# CREAR PUBLICACIÓN
# ======================================================

def crear_publicacion(publicacion):

    try:

        inicio_publicacion = time.time()

        abrir_formulario()

        completar_formulario(publicacion)

        if not subir_imagenes(
            driver,
            publicacion["ruta_imagen"]
        ):

            raise Exception("Falló la subida de imágenes.")

        publicar()

        # Intentar cerrar popup (si aparece)
        cerrar_popup()

        # Esperar que la página vuelva al inicio
        esperar_click(
            By.XPATH,
            "//p[contains(text(),'Publicar nuevo producto')]"
        )

        pausa_humana(inicio_publicacion)

        publicaciones_ok.append(
            publicacion["titulo"]
        )

    except Exception:

        traceback.print_exc()

        publicaciones_error.append(

            (
                publicacion["titulo"],
                "Error al publicar"
            )

        )

        cerrar_formulario()

# ======================================================
# RESUMEN
# ======================================================

def mostrar_resumen(inicio):

    titulo("RESUMEN FINAL")

    tiempo = round(time.time() - inicio, 1)

    print(f"Tiempo total: {tiempo} segundos")
    print()

    print(f"Publicaciones exitosas: {len(publicaciones_ok)}")

    if publicaciones_ok:

        for p in publicaciones_ok:

            print(f"   ✅ {p}")

    print()

    print(f"Errores: {len(publicaciones_error)}")

    if publicaciones_error:

        print()

        for titulo_error, motivo in publicaciones_error:

            print(f"   ❌ {titulo_error}")

            print(f"      {motivo}")

    print()

# ======================================================
# MAIN
# ======================================================

def leer_argumentos():

    parser = argparse.ArgumentParser(
        description="Sube publicaciones a Avellaneda a un Toque desde un CSV."
    )

    parser.add_argument(
        "--conservar-existentes",
        action="store_true",
        help=(
            "No borra las publicaciones actuales. "
            "Por defecto se borran TODAS antes de subir las nuevas."
        )
    )

    return parser.parse_args()


def main():

    global driver

    argumentos = leer_argumentos()

    inicio = time.time()

    titulo("SCRIPT AVELLANEDA A UN TOQUE")

    driver = iniciar_navegador()

    try:

        publicaciones = cargar_publicaciones()

        if len(publicaciones) == 0:

            aviso("No existen publicaciones para subir.")

            return

        login()

        if argumentos.conservar_existentes:

            aviso(
                "Se mantienen las publicaciones existentes "
                "(se usó --conservar-existentes)."
            )

        else:

            eliminar_publicaciones()

        total = len(publicaciones)

        for numero, publicacion in enumerate(publicaciones, start=1):

            titulo(f"PRODUCTO {numero} DE {total}")

            crear_publicacion(publicacion)

        mostrar_resumen(inicio)

    except Exception:

        traceback.print_exc()

    finally:

        print()

        input("Presione ENTER para cerrar el navegador...")

        driver.quit()


if __name__ == "__main__":

    main()
