"""
Scraping de Televisores – Plaza Vea
Recorre 50 páginas, extrae datos completos incluyendo imágenes.
Guarda CSV con separador “;” para que cada valor caiga en su columna.
"""

import csv, os, time, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ---------- CONFIGURAR RUTA DE CHROMEDRIVER ----------
chrome_path = r"D:\DATOS\WEB SCRAPING\PLAZA VEA\chrome driver\chromedriver-win64\chromedriver-win64\chromedriver.exe"
# -----------------------------------------------------

# ---------- OPCIONES ----------
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(chrome_path), options=options)

# ---------- FUNCIONES ----------
def safe_text(el, css):
    try:
        return el.find_element(By.CSS_SELECTOR, css).text.strip()
    except:
        return ""

def clean_price(txt: str) -> str:
    if not txt:
        return ""
    txt = re.sub(r"[^\d,\.]", "", txt)
    txt = txt.replace(".", "")
    txt = txt.replace(",", ".")
    return txt

# ---------- SCRAPING PAGINADO ----------
data = []
for page in range(1, 51):  # páginas del 1 al 50
    url = f"https://www.plazavea.com.pe/tecnologia/televisores?page={page}"
    print(f"Procesando página {page}...")
    driver.get(url)
    time.sleep(3)

    # Scroll lento para asegurar carga de imágenes
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(0.5)

    selector = "div.HA.Showcase.Showcase--non-food.ga-product-item"
    products = driver.find_elements(By.CSS_SELECTOR, selector)

    for p in products:
        precio_actual  = clean_price(safe_text(p, ".Showcase__salePrice .price"))
        precio_antiguo = clean_price(safe_text(p, ".Showcase__oldPrice .price"))
        precio_oh      = clean_price(safe_text(p, ".Showcase__ohPrice .price"))

        # Intentar forzar carga de imagen si está lazy-loaded
        try:
            img_el = p.find_element(By.CSS_SELECTOR, ".Showcase__photo img")
            img_url = (
                img_el.get_attribute("src")
                or img_el.get_attribute("data-src")
                or img_el.get_attribute("data-lazy")
                or ""
            )
            if not img_url:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", p)
                time.sleep(0.5)
                img_url = (
                    img_el.get_attribute("src")
                    or img_el.get_attribute("data-src")
                    or img_el.get_attribute("data-lazy")
                    or ""
                )
        except:
            img_url = ""

        data.append({
            "Nombre":        p.get_attribute("data-ga-name")      or "",
            "Marca":         p.get_attribute("data-ga-brand")     or "",
            "Precio_actual": precio_actual,
            "Precio_antiguo": precio_antiguo,
            "Precio_Oh":     precio_oh,
            "SKU":           p.get_attribute("data-sku")          or "",
            "Categoria":     p.get_attribute("data-ga-category")  or "",
            "Enlace":        p.find_element(By.CSS_SELECTOR, ".Showcase__link").get_attribute("href"),
            "Stock":         "Sí" if p.get_attribute("data-stock") == "true" else "No",
            "Imagen_URL":    img_url
        })

driver.quit()

# ---------- GUARDAR CSV ----------
fieldnames = ["Nombre", "Marca", "Precio_actual", "Precio_antiguo", "Precio_Oh",
              "SKU", "Categoria", "Enlace", "Stock", "Imagen_URL"]

ruta_csv = input(
    "\n📁 Ruta completa para guardar CSV (enter = Escritorio/televisores_plazavea.csv):\n> "
).strip('"').strip("'").strip()

if not ruta_csv:
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    ruta_csv = os.path.join(escritorio, "televisores_plazavea.csv")

os.makedirs(os.path.dirname(ruta_csv), exist_ok=True)

with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
        delimiter=";", quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    writer.writerows(data)

print(f"\n✅ Datos guardados en: {ruta_csv}")


