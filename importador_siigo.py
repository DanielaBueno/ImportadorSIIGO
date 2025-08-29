import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import openpyxl
from openpyxl.styles import numbers
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
import logging

# Siempre usar la carpeta donde está el ejecutable/script como base
os.chdir(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__))

# Configuración de logging
log_path = os.path.join(os.getcwd(), "siigo_log.txt")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Obtener la ruta al archivo plantilla incluido con el ejecutable
def obtener_ruta_recurso(nombre_archivo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_archivo)  # Para PyInstaller
    return os.path.join(os.path.abspath("."), nombre_archivo)

archivo1 = ""
archivo2 = ""
plantilla = obtener_ruta_recurso("plantilla_siigo.xlsx")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Herramienta de Importación SIIGO")
ventana.geometry("450x500")
# Establecer ícono de ventana
try:
    ventana.iconbitmap(obtener_ruta_recurso("icono.ico"))
except FileNotFoundError:
    logging.warning("No se pudo cargar el icono")
    pass  # No se encontró ícono, continuar sin él

def seleccionar_archivo(tipo):
    global archivo1, archivo2, plantilla
    ruta = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if tipo == "r1":
        archivo1 = ruta
        print("📄 Archivo 1 seleccionado:", archivo1)
        lbl_r1.config(text="✔ Reporte 1 cargado")
        logging.info("Reporte 1 cargado: %s", archivo1)
    elif tipo == "r2":
        archivo2 = ruta
        print("📄 Archivo 2 seleccionado:", archivo2)
        lbl_r2.config(text="✔ Reporte 2 cargado")
        logging.info("Reporte 2 cargado: %s", archivo2)


def ejecutar():
    try:
        if not archivo1 or not archivo2 or not plantilla:
            messagebox.showerror("Error", "Debes cargar todos los archivos.")
            logging.error("Faltan archivos por cargar.")
            return
        
        if not os.path.exists(archivo1):
            raise FileNotFoundError(f"El archivo Reporte 1 no fue encontrado: {archivo1}")
        if not os.path.exists(archivo2):
            raise FileNotFoundError(f"El archivo Reporte 2 no fue encontrado: {archivo2}")

        # Cargar Reporte 1
        def cargar_hoja_con_columnas(archivo, columnas_esperadas):
            try:
                # Detectar motor según extensión
                if archivo.lower().endswith(".xls"):
                    with open(archivo, "rb") as f:
                        inicio = f.read(1024)
                    if b"<table" in inicio.lower():  # 👈 Es un HTML disfrazado de .xls
                        df_list = pd.read_html(archivo)  # Devuelve lista de tablas
                        for df in df_list:
                            if all(col in df.columns for col in columnas_esperadas):
                                return df
                        raise ValueError(f"No se encontró una tabla con las columnas requeridas en {archivo}.")
                    else:
                        xls = pd.ExcelFile(archivo, engine="xlrd")
                else:
                    xls = pd.ExcelFile(archivo, engine="openpyxl")

                for nombre_hoja in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=nombre_hoja, engine='openpyxl' if archivo.endswith('.xlsx') else 'xlrd')
                    if all(col in df.columns for col in columnas_esperadas):
                        return df
                    
                columnas_encontradas = df.columns.tolist()
                columnas_faltantes = [col for col in columnas_esperadas if col not in columnas_encontradas]

                raise ValueError(f"No se encontró una hoja con las columnas requeridas en {archivo}.")
            except Exception as e:
                logging.error("Error cargando hoja desde %s: %s", archivo, e)
                raise

        # Cargar Reporte 1 sin importar el nombre de la hoja
        columnas_r1 = ["factura", "codigo", "referencia", "cantidad", "valor_total"]
        r1 = cargar_hoja_con_columnas(archivo1, columnas_r1)
        logging.info("Reporte 1 cargado con %d registros.", len(r1))

        # Filtrar filas donde 'valor_total' es 0
        r1 = r1[r1["valor_total"] != 0]
        logging.info("Reporte 1 después de filtrar valor_total=0: %d registros.", len(r1))

        # Agregar la columna 'Valor unitario' calculando la división de 'valor_total' por 'cantidad'
        r1["Valor unitario"] = r1["valor_total"] / r1["cantidad"]

        # Renombrar columnas
        r1 = r1.rename(columns={
            "factura": "Consecutivo",
            "codigo": "Código producto",
            "referencia": "Descripción producto",
            "cantidad": "Cantidad producto"
        })
        r1 = r1[["Consecutivo", "Código producto", "Descripción producto", "Cantidad producto", "Valor unitario"]]
        r1["Consecutivo"] = r1["Consecutivo"].astype(str)

        # Cargar Reporte 2 sin importar el nombre de la hoja
        columnas_r2 = ["NitEmpresa", "f_fact", "numero", "total"]
        r2 = cargar_hoja_con_columnas(archivo2, columnas_r2)
        logging.info("Reporte 2 cargado con %d registros.", len(r2))

        print(f"Columnas del Reporte 2: {r2.columns.tolist()}")

        # **IMPORTANTE: Filtro por usuario ANTES del merge**
        usuario_filtro = usuario_entry.get().strip()
        if usuario_filtro:
            if "usuario" in r2.columns:
                r2_original_count = len(r2)
                r2 = r2[r2["usuario"].str.contains(usuario_filtro, case=False, na=False)]
                logging.info("Filtrado por usuario: %s (De %d a %d registros)", usuario_filtro, r2_original_count, len(r2))
                print(f"🔍 Filtro de usuario aplicado: {r2_original_count} → {len(r2)} registros")
            else:
                logging.warning("Se intentó filtrar por usuario, pero la columna 'usuario' no existe en el Reporte 2.")
                print("⚠️ Advertencia: No se encontró la columna 'usuario' en el Reporte 2")

        # Renombrar columnas de Reporte 2
        r2 = r2.rename(columns={
            "NitEmpresa": "Identificación tercero",
            "f_fact": "Fecha de elaboración",
            "numero": "Consecutivo",
            "total": "Valor Forma de Pago"
        })
        r2 = r2[["Consecutivo", "Identificación tercero", "Fecha de elaboración", "Valor Forma de Pago"]]
        r2["Consecutivo"] = r2["Consecutivo"].astype(str)

        print(f"📊 Registros antes del merge - R1: {len(r1)}, R2: {len(r2)}")

        # **COMBINAR CON LEFT JOIN PERO CONTROLADO**
        df = pd.merge(r1, r2, on="Consecutivo", how="left")
        logging.info("Registros después del merge: %d", len(df))
        print(f"🔗 Registros después del merge: {len(df)}")

        # **VERIFICAR REGISTROS SIN COINCIDENCIA**
        registros_sin_coincidencia = df[df["Identificación tercero"].isna()]
        if len(registros_sin_coincidencia) > 0:
            consecutivos_sin_coincidencia = registros_sin_coincidencia["Consecutivo"].unique()
            logging.warning("Se encontraron %d registros sin coincidencia en R2. Consecutivos: %s", 
                          len(registros_sin_coincidencia), str(consecutivos_sin_coincidencia[:10]))
            print(f"⚠️ {len(registros_sin_coincidencia)} registros sin coincidencia en R2")
            print(f"Primeros consecutivos sin coincidencia: {consecutivos_sin_coincidencia[:5]}")

        # **FILTRO Y LIMPIEZA - MANTENER SOLO REGISTROS CON DATOS COMPLETOS**
        print(f"📋 Registros antes de filtros de limpieza: {len(df)}")
        
        # Solo mantener registros que tienen datos del Reporte 2 (no NaN)
        df = df.dropna(subset=["Identificación tercero", "Fecha de elaboración", "Valor Forma de Pago"])
        print(f"📋 Registros después de eliminar NaN: {len(df)}")
        logging.info("Registros después de eliminar NaN: %d", len(df))

        # Filtro por consecutivos que empiecen con E o e
        df = df[df["Consecutivo"].astype(str).str.startswith(("E", "e"))]
        print(f"📋 Registros después de filtrar por E/e: {len(df)}")
        logging.info("Registros después de filtrar por E/e: %d", len(df))

        # Limpiar el consecutivo eliminando E/e del inicio
        df["Consecutivo"] = df["Consecutivo"].astype(str).str.lstrip("Ee")
        
        # Limpiar identificación tercero (quitar parte después del guión)
        df["Identificación tercero"] = df["Identificación tercero"].astype(str).str.split("-").str[0]
        
        # Convertir fecha a formato date
        df["Fecha de elaboración"] = pd.to_datetime(df["Fecha de elaboración"]).dt.date

        print(f"📋 Registros finales después de limpieza: {len(df)}")
        logging.info("Registros finales después de limpieza: %d", len(df))

        if len(df) == 0:
            raise ValueError("No quedaron registros después de aplicar los filtros. Verifique:\n"
                           "1. Que el filtro de usuario sea correcto\n"
                           "2. Que existan consecutivos que empiecen con 'E'\n"
                           "3. Que haya coincidencias entre ambos reportes")

        # Plantilla final
        columnas_objetivo = [
            "Tipo de comprobante", "Consecutivo", "Identificación tercero", "Sucursal", "Código centro/subcentro de costos",
            "Fecha de elaboración", "Sigla Moneda", "Tasa de cambio", "Nombre contacto", "Email Contacto",
            "Orden de compra", "Orden de entrega", "Fecha orden de entrega", "Código producto", "Descripción producto",
            "Identificación vendedor", "Código de Bodega", "Cantidad producto", "Valor unitario", "Valor Descuento", "Base AIU",
            "Identificación ingreso para terceros", "Código impuesto cargo", "Código impuesto cargo dos",
            "Código impuesto retención", "Código ReteICA", "Código ReteIVA", "Código forma de pago",
            "Valor Forma de Pago", "Fecha Vencimiento", "Observaciones"
        ]

        for col in columnas_objetivo:
            if col not in df.columns:
                df[col] = ""

        df["Tipo de comprobante"] = 1
        df["Identificación vendedor"] = 807001777

        if var_fecha_vencimiento.get():
            df["Fecha Vencimiento"] = df["Fecha de elaboración"]
            logging.info("Fecha de elaboración copiada a Fecha Vencimiento.")

        df = df[columnas_objetivo]

        # Asignar Valor Forma de Pago solo en la primera fila de cada grupo por 'Consecutivo'
        df['Valor Forma de Pago'] = df.groupby('Consecutivo')['Valor Forma de Pago'].transform('first')
        # Que los demás valores sean vacíos en filas duplicadas:
        df.loc[df.duplicated('Consecutivo'), 'Valor Forma de Pago'] = ''

        # Crear carpeta "exportados" si no existe
        carpeta_exportados = os.path.join(os.getcwd(), "Exportados SIIGO")
        os.makedirs(carpeta_exportados, exist_ok=True)

        # Nombre del archivo con fecha y hora
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archivo_salida = os.path.join(carpeta_exportados, f"SIIGO_Ingresos_{fecha_hora}.xlsx")

        # Cargar la plantilla
        wb = openpyxl.load_workbook(plantilla)
        ws = wb.active

        # Limpiar todo menos el encabezado
        ws.delete_rows(2, ws.max_row)

        # Agregar los datos del DataFrame a partir de la fila 2
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
            for c_idx, value in enumerate(row, start=1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)

                # Copiar solo los estilos básicos del encabezado
                if r_idx == 1:
                    header_cell = ws.cell(row=1, column=c_idx)
                    if hasattr(header_cell, 'fill'):
                        cell.fill = header_cell.fill.copy()
                    if hasattr(header_cell, 'font'):
                        cell.font = header_cell.font.copy()
                    if hasattr(header_cell, 'border'):
                        cell.border = header_cell.border.copy()
                    if hasattr(header_cell, 'alignment'):
                        cell.alignment = header_cell.alignment.copy()
                    if hasattr(header_cell, 'number_format'):
                        cell.number_format = header_cell.number_format

        # Asegurar formato de fecha
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=columnas_objetivo.index("Fecha de elaboración") + 1, max_col=columnas_objetivo.index("Fecha de elaboración") + 1):
            for cell in row:
                if isinstance(cell.value, datetime):
                    cell.number_format = 'YYYY-MM-DD'

        wb.save(archivo_salida)
        logging.info("Archivo generado correctamente: %s", archivo_salida)
        messagebox.showinfo("¡Éxito!", f"Archivo generado con {len(df)} registros:\n{archivo_salida}")

    except Exception as e:
        logging.exception("Error durante la ejecución")
        messagebox.showerror("Error durante el proceso", str(e))

# Botones de selección de archivos
tk.Button(ventana, text="📂 Cargar Reporte 1", command=lambda: seleccionar_archivo("r1")).pack(pady=5)
lbl_r1 = tk.Label(ventana, text="⏳ Esperando archivo...", fg="gray")
lbl_r1.pack()

tk.Button(ventana, text="📂 Cargar Reporte 2", command=lambda: seleccionar_archivo("r2")).pack(pady=5)
lbl_r2 = tk.Label(ventana, text="⏳ Esperando archivo...", fg="gray")
lbl_r2.pack()

#Filtar por usuario
tk.Label(ventana, text="Filtrar por usuario:").pack()
usuario_entry = tk.Entry(ventana)
usuario_entry.pack(pady=5)

#Checkbox fecha de elaboración a Fecha de Vencimiento
var_fecha_vencimiento = tk.BooleanVar()
tk.Checkbutton(ventana, text="✅ Copiar Fecha de elaboración a Fecha Vencimiento", variable=var_fecha_vencimiento).pack(pady=10)

# Botón ejecutar
tk.Button(ventana, text="✅ Ejecutar", bg="#4CAF50", fg="white", command=ejecutar).pack(pady=20)

ventana.mainloop()
