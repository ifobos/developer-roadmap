# Convertidor de JSON a CSV para Roadmaps

Este script convierte los archivos JSON de los roadmaps en tablas CSV para facilitar el análisis de datos.

## Archivos generados

El script genera los siguientes archivos en la carpeta `csv_output/`:

### Archivos individuales por roadmap
- `{roadmap_name}_nodes.csv` - Un archivo CSV por cada roadmap con todos sus nodos
- Cada archivo contiene información detallada de los nodos: ID, tipo, posición, dimensiones, etiquetas, estilos, etc.

### Archivos consolidados
- `all_roadmaps_nodes.csv` - Archivo consolidado con todos los nodos de todos los roadmaps
- `roadmaps_summary.csv` - Resumen con estadísticas de cada roadmap

## Estructura de datos en los CSV

Cada archivo CSV de nodos contiene las siguientes columnas:

### Información básica del nodo
- **roadmap**: Nombre del roadmap
- **id**: ID único del nodo
- **type**: Tipo de nodo (topic, subtopic, section, title, vertical, etc.)
- **position_x, position_y**: Coordenadas de posición
- **width, height**: Dimensiones del nodo
- **label**: Texto/etiqueta del nodo

### Relaciones jerárquicas
- **parent_id**: ID del nodo padre (basado en las conexiones edges del JSON)
- **parent_label**: Etiqueta/nombre del nodo padre

### Archivos de contenido (NUEVO)
- **content_file_path**: Ruta del archivo de contenido relacionado (.md) si existe

### Propiedades de estado y estilo
- **selected, dragging**: Estados booleanos
- **zIndex**: Índice de profundidad
- **fontSize**: Tamaño de fuente
- **backgroundColor, borderColor**: Colores de fondo y borde
- **stroke, strokeWidth**: Propiedades de trazo
- **textAlign**: Alineación del texto

### Análisis de relaciones

Las columnas `parent_id` y `parent_label` permiten:
- Identificar nodos raíz (sin padre)
- Construir árboles jerárquicos
- Analizar rutas de aprendizaje
- Calcular profundidad de conceptos

## Archivos de contenido relacionados

La columna `content_file_path` establece la conexión entre los nodos del roadmap y su documentación:
- **Patrón de nomenclatura**: Los archivos siguen el formato `nombre-del-tema@{ID_DEL_NODO}.md`
- **Ubicación**: Se encuentran en `src/data/roadmaps/{roadmap}/content/`
- **Ejemplo**: El nodo con ID `Tv8-WUcKiZMLHuunQwise` se relaciona con `dependency-manager@Tv8-WUcKiZMLHuunQwise.md`
- **Contenido**: Cada archivo contiene información detallada, recursos y enlaces sobre el tema específico
- **Uso**: Permite acceder directamente a la documentación completa de cada concepto del roadmap

## Requisitos

- Python 3.x
- pandas (instalado automáticamente)

## Uso

### Instalación y ejecución

1. **Navegar a la carpeta InterviewTemplates**:
   ```bash
   cd InterviewTemplates
   ```

2. **Crear entorno virtual** (recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En macOS/Linux
   # o
   venv\Scripts\activate     # En Windows
   ```

3. **Instalar dependencias**:
   ```bash
   pip install pandas
   ```

4. **Ejecutar el convertidor principal**:
   ```bash
   python json_to_csv_converter.py
   ```

5. **Validar la integridad de los datos** (recomendado):
   ```bash
   # Validación completa
   python validate_content_files.py
   
   # Corrección automática si es necesario
   python fix_content_references.py
   
   # Resumen rápido del estado
   python validation_summary.py
   ```

6. **Generar archivos Excel para entrevistas**:
   ```bash
   # Instalar dependencia adicional
   pip install openpyxl
   
   # Generar archivos Excel usando plantilla
   python generate_excel_from_csv.py
   ```

7. **Ejecutar análisis y demos** (opcional):
   ```bash
   # Demo de análisis jerárquico
   python demo_hierarchy.py
   
   # Demo de archivos de contenido
   python demo_content_files.py
   
   # Análisis avanzado de jerarquías
   python analyze_hierarchy.py
   ```

### Resultados

El script procesará todos los archivos JSON en `src/data/roadmaps/` y generará:

- **55+ archivos CSV individuales** (uno por roadmap)
- **1 archivo consolidado** con todos los nodos
- **1 archivo de resumen** con estadísticas
- **57 archivos Excel** (opcional, usando el generador de plantillas)

## Estadísticas del último procesamiento

- **Total de archivos JSON procesados**: 106
- **Total de nodos extraídos**: 8,774
- **Roadmaps procesados**: 56
- **Archivos CSV generados**: 55+ individuales + 1 consolidado + 1 resumen
- **Nodos con archivos de contenido**: 6,366 (72.5% de cobertura)
- **Tipos de nodos con contenido**: subtopic (5,301), topic (1,048), todo (17)

## Ejemplos de uso de los datos

Con los archivos CSV generados puedes:

1. **Análisis en Excel/Google Sheets**: Abrir directamente los archivos CSV
2. **Análisis con Python/pandas**:
   ```python
   import pandas as pd
   
   # Cargar todos los nodos
   df = pd.read_csv('csv_output/all_roadmaps_nodes.csv')
   
   # Análisis por tipo de nodo
   print(df['type'].value_counts())
   
   # Análisis por roadmap
   print(df['roadmap'].value_counts())
   
   # Analizar nodos con contenido disponible
   nodos_con_contenido = df[df['content_file_path'].notna() & (df['content_file_path'] != '')]
   print(f"Nodos con archivo de contenido: {len(nodos_con_contenido)}")
   print(f"Porcentaje de cobertura: {len(nodos_con_contenido)/len(df)*100:.1f}%")
   ```

### Acceso a archivos de contenido
```python
# Encontrar nodos con contenido específico
ios_df = df[df['roadmap'] == 'ios']
nodos_con_contenido = ios_df[ios_df['content_file_path'].notna() & (ios_df['content_file_path'] != '')]

# Mostrar relación nodo-archivo
for _, row in nodos_con_contenido.head().iterrows():
    print(f"Nodo: {row['label']} -> Archivo: {row['content_file_path']}")

# Leer contenido de un archivo específico
import os
if os.path.exists(nodos_con_contenido.iloc[0]['content_file_path']):
    with open(nodos_con_contenido.iloc[0]['content_file_path'], 'r', encoding='utf-8') as f:
        contenido = f.read()
        print(f"Contenido del archivo: {contenido[:200]}...")
```

3. **Visualización de datos**: Usar los datos para crear gráficos y dashboards
4. **Análisis de contenido**: Analizar las etiquetas y estructura de los roadmaps

## Estructura de directorios

```
InterviewTemplates/
├── json_to_csv_converter.py     # Script principal
├── validate_content_files.py    # Validación de archivos de contenido
├── fix_content_references.py    # Corrección automática de referencias
├── validation_summary.py        # Resumen de validación
├── generate_excel_from_csv.py   # Generador de archivos Excel
├── verify_excel_output.py       # Verificación de archivos Excel
├── demo_hierarchy.py            # Demo de análisis jerárquico
├── demo_content_files.py        # Demo de archivos de contenido
├── analyze_hierarchy.py         # Análisis avanzado de jerarquías
├── requirements.txt             # Dependencias
├── README_CSV_CONVERTER.md      # Este archivo
├── venv/                        # Entorno virtual (creado al ejecutar)
├── csv_output/                  # Archivos CSV generados
│   ├── ios_nodes.csv
│   ├── android_nodes.csv
│   ├── react_nodes.csv
│   ├── ...
│   ├── all_roadmaps_nodes.csv
│   └── roadmaps_summary.csv
└── Interviews/                  # Archivos relacionados con entrevistas
    ├── InterviewTemplate.xlsx   # Plantilla base para Excel
    └── generated/               # Archivos Excel generados
        ├── ios_interview_template.xlsx
        ├── android_interview_template.xlsx
        ├── react_interview_template.xlsx
        └── ...
```

## Scripts de Validación y Mantenimiento

Además del convertidor principal, se incluyen scripts adicionales para validar y mantener la integridad de los datos:

### validate_content_files.py
Script de validación que verifica la correcta asociación entre nodos y archivos de contenido:
```bash
python validate_content_files.py
```

**Funcionalidades:**
- Encuentra todos los archivos de contenido `.md` en los roadmaps
- Verifica las referencias en la columna `content_file_path` de los CSV
- Identifica archivos no referenciados y referencias inválidas
- Genera reportes detallados por roadmap con estadísticas de cobertura

### fix_content_references.py
Script de corrección automática para resolver inconsistencias:
```bash
python fix_content_references.py
```

**Funcionalidades:**
- Elimina duplicados en los archivos CSV
- Corrige referencias inválidas de archivos de contenido
- Agrega referencias faltantes automáticamente
- Procesa todos los archivos CSV de forma batch

### validation_summary.py
Script de resumen que proporciona una vista concisa del estado de validación:
```bash
python validation_summary.py
```

**Funcionalidades:**
- Genera un resumen ejecutivo del estado de validación
- Identifica roadmaps problemáticos que requieren atención
- Calcula ratios de cobertura y estadísticas generales
- Proporciona una vista rápida del estado del sistema

### generate_excel_from_csv.py
Script que genera archivos Excel individuales para cada roadmap usando una plantilla:
```bash
python generate_excel_from_csv.py
```

**Funcionalidades:**
- Utiliza `Interviews/InterviewTemplate.xlsx` como plantilla base
- Genera un archivo Excel por cada archivo CSV en `csv_output/`
- Mapea automáticamente las columnas `roadmap`, `label` y `content_file_path`
- Preserva las fórmulas y formato de la plantilla
- Guarda los archivos en `Interviews/generated/` con formato `{roadmap}_interview_template.xlsx`

**Dependencias adicionales:**
```bash
pip install openpyxl
```

### demo_hierarchy.py
Script de demostración que muestra análisis jerárquico de los roadmaps:
```bash
python demo_hierarchy.py
```

**Funcionalidades:**
- Analiza la estructura jerárquica de todos los roadmaps
- Identifica nodos con más hijos (conceptos más amplios)
- Calcula métricas de profundidad y complejidad
- Muestra roadmaps con mayor estructura jerárquica
- Proporciona ejemplos prácticos de análisis de datos

### demo_content_files.py
Script de demostración que muestra el análisis de archivos de contenido:
```bash
python demo_content_files.py
```

**Funcionalidades:**
- Demuestra cómo acceder a archivos de contenido desde los CSV
- Muestra estadísticas de cobertura de contenido por roadmap
- Ejemplifica la lectura y procesamiento de archivos markdown
- Proporciona casos de uso prácticos para análisis de contenido

### analyze_hierarchy.py
Script de análisis avanzado con opciones interactivas:
```bash
python analyze_hierarchy.py
```

**Funcionalidades:**
- Análisis interactivo de todos los roadmaps o uno específico
- Búsqueda de rutas de aprendizaje entre conceptos
- Análisis de dependencias y prerrequisitos
- Identificación de conceptos fundamentales vs. avanzados
- Generación de reportes detallados de estructura jerárquica

### Resultados de Validación

**Estado actual del sistema:**
- ✅ **6,315 de 6,659 archivos** correctamente referenciados (94.8% cobertura)
- ✅ **53 roadmaps** con buena cobertura (89-100%)
- ⚠️ **5 roadmaps** que requieren atención: devops, docker, frontend, golang, prompt-engineering
- 📄 **296 archivos huérfanos** identificados para posible limpieza

## Notas

- El script procesa automáticamente todos los archivos `.json` encontrados en las subcarpetas de `src/data/roadmaps/`
- Los archivos `migration-mapping.json` se procesan pero generalmente no contienen nodos
- Los archivos CSV se generan con codificación UTF-8 para soportar caracteres especiales
- Si un roadmap no tiene nodos, no se genera archivo CSV individual para ese roadmap
- Las referencias múltiples (200% cobertura) son normales cuando varios nodos comparten el mismo contenido
- Se recomienda ejecutar los scripts de validación periódicamente para mantener la integridad del sistema