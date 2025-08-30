# ImportadorSIIGO
Aplicación en Python que automatiza el completar  la plantilla de facturación del sistema SIIGO a partir de los reportes descargados del sistema Sofia de Colmedicos 
# Herramienta de Importación SIIGO v2

Una aplicación de escritorio moderna desarrollada en Python que automatiza el procesamiento y combinación de reportes Excel para su importación al sistema contable SIIGO.

## Características

- **Interfaz Moderna**: Desarrollada con CustomTkinter con tema oscuro/claro
- **Procesamiento Automatizado**: Combina datos de dos reportes Excel diferentes
- **Filtrado Avanzado**: Permite filtrar por usuario con opciones de coincidencia exacta
- **Validación de Datos**: Verifica la integridad de los datos antes del procesamiento
- **Exportación Lista**: Genera archivos Excel compatibles con SIIGO
- **Logging Detallado**: Registra todas las operaciones para auditoría

## Requisitos del Sistema

- Windows 10/11
- Python 3.8 o superior
- 4GB RAM mínimo
- 100MB espacio libre en disco

## Instalación

### Para Usuarios (Ejecutable)

1. Descargar el archivo `SIIGO_Tool_v2.exe` desde [Releases](releases)
2. Ejecutar como administrador
3. Seguir las instrucciones del instalador

### Para Desarrolladores

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/herramienta-siigo-v2.git
cd herramienta-siigo-v2

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

## Dependencias

```
pandas>=2.0.0
customtkinter>=5.2.0
openpyxl>=3.1.0
tkinter (incluido en Python)
```

## Uso

### 1. Preparación de Archivos

Asegúrate de tener:
- **Reporte 1 (Productos)**: Archivo Excel con columnas: `factura`, `codigo`, `referencia`, `cantidad`, `valor_total`
- **Reporte 2 (Facturas)**: Archivo Excel con columnas: `NitEmpresa`, `f_fact`, `numero`, `total`, `usuario` (opcional)
- **Plantilla SIIGO**: Archivo `plantilla_siigo.xlsx` en la carpeta de la aplicación

### 2. Ejecutar el Proceso

1. **Cargar Reportes**: Usar los botones "Cargar Reporte 1" y "Cargar Reporte 2"
2. **Configurar Filtros** (opcional):
   - Filtrar por usuario específico
   - Configurar opciones de coincidencia
   - Activar copia de fecha de vencimiento
3. **Ejecutar**: Hacer clic en "EJECUTAR PROCESO"
4. **Resultado**: El archivo procesado se guardará en la carpeta `Exportados SIIGO/`

### 3. Importar a SIIGO

1. Abrir SIIGO
2. Ir a Importación de Datos
3. Seleccionar el archivo generado
4. Seguir el asistente de importación

## Estructura del Proyecto

```
herramienta-siigo-v2/
├── main.py                 # Archivo principal
├── plantilla_siigo.xlsx    # Plantilla base de SIIGO
├── icono.ico              # Ícono de la aplicación
├── requirements.txt        # Dependencias
├── Exportados SIIGO/      # Carpeta de salida (se crea automáticamente)
├── docs/                  # Documentación
│   ├── analisis.md
│   └── backlog.md
├── tests/                 # Pruebas unitarias
└── build/                 # Archivos de compilación
```

## Funcionalidades Técnicas

### Procesamiento de Datos

- **Limpieza automática**: Elimina registros con valores nulos o inconsistentes
- **Transformación**: Calcula valores unitarios y reorganiza columnas
- **Validación**: Verifica que los consecutivos empiecen con 'E'
- **Combinación**: Une datos por número de consecutivo

### Filtrado de Usuarios

- **Búsqueda flexible**: Coincidencia parcial o exacta
- **Sensibilidad a mayúsculas**: Configurable
- **Vista previa**: Muestra usuarios disponibles antes de filtrar
- **Estadísticas**: Informa cantidad de registros procesados

### Exportación

- **Formato SIIGO**: Compatible con plantillas oficiales
- **Preservación de formato**: Mantiene estilos de la plantilla
- **Fecha automática**: Nombres de archivo con timestamp
- **Organización**: Archivos en carpeta dedicada

## Logs y Auditoría

La aplicación genera un archivo `siigo_log.txt` que registra:
- Archivos cargados
- Filtros aplicados
- Número de registros procesados
- Errores y advertencias
- Archivos generados

## Solución de Problemas

### Errores Comunes

**"No se encontraron las columnas requeridas"**
- Verificar que los archivos Excel tengan las columnas correctas
- Revisar nombres de columnas (sensible a mayúsculas/minúsculas)

**"El filtro eliminó todos los registros"**
- Verificar que el nombre de usuario existe en el Reporte 2
- Usar la función "Ver Usuarios" para confirmar nombres exactos

**"No quedaron registros después de los filtros"**
- Verificar que existan consecutivos que empiecen con 'E'
- Revisar que haya coincidencias entre ambos reportes

### Contacto para Soporte

- **Issues**: [GitHub Issues](issues)
- **Email**: tu-email@ejemplo.com
- **Documentación**: Ver carpeta `docs/`

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Changelog

### v2.0.0 (2025-08-30)
- Refactorización completa del código
- Interfaz moderna con CustomTkinter
- Mejor manejo de errores
- Documentación completa
- Filtrado avanzado de usuarios

### v1.0.0 (Fecha anterior)
- Versión inicial
- Funcionalidad básica de procesamiento

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.

## Reconocimientos

- **CustomTkinter**: Por la moderna librería de UI
- **pandas**: Por las potentes herramientas de procesamiento de datos
- **openpyxl**: Por el manejo de archivos Excel
- **Comunidad Python**: Por las herramientas y documentación

---

**Nota**: Esta herramienta es independiente y no está oficialmente afiliada con SIIGO. Es una utilidad desarrollada para facilitar el proceso de importación de datos.
