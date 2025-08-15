#!/usr/bin/env python3
"""
Script de validación para verificar que todos los archivos de contenido
estén correctamente referenciados en los archivos CSV generados.
"""

import os
import pandas as pd
from pathlib import Path
import glob

def find_all_content_files(roadmaps_dir):
    """
    Encuentra todos los archivos de contenido .md en las carpetas de roadmaps
    """
    content_files = []
    roadmaps_path = Path(roadmaps_dir)
    
    # Buscar en cada roadmap
    for roadmap_dir in roadmaps_path.iterdir():
        if roadmap_dir.is_dir():
            content_dir = roadmap_dir / 'content'
            if content_dir.exists():
                # Buscar archivos .md en la carpeta content
                md_files = list(content_dir.glob('*.md'))
                for md_file in md_files:
                    # Extraer el ID del archivo (parte después del @)
                    filename = md_file.name
                    if '@' in filename:
                        parts = filename.split('@')
                        if len(parts) == 2:
                            node_id = parts[1].replace('.md', '')
                            # Calcular ruta relativa de forma segura
                            try:
                                relative_path = str(md_file.relative_to(Path.cwd()))
                            except ValueError:
                                # Si no se puede calcular relativa al directorio actual, usar ruta absoluta
                                relative_path = str(md_file)
                            
                            content_files.append({
                                'roadmap': roadmap_dir.name,
                                'file_path': str(md_file),
                                'relative_path': relative_path,
                                'node_id': node_id,
                                'filename': filename
                            })
    
    return content_files

def load_csv_content_references(csv_dir):
    """
    Carga todas las referencias de archivos de contenido desde los archivos CSV
    """
    csv_references = []
    csv_path = Path(csv_dir)
    
    # Buscar todos los archivos CSV de nodos (excluyendo summary)
    csv_files = list(csv_path.glob('*_nodes.csv'))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            # Verificar si existe la columna content_file_path
            if 'content_file_path' in df.columns:
                # Filtrar filas que tienen contenido
                content_rows = df[df['content_file_path'].notna() & (df['content_file_path'] != '')]
                
                for _, row in content_rows.iterrows():
                    csv_references.append({
                        'roadmap': row['roadmap'],
                        'node_id': row['id'],
                        'node_label': row['label'],
                        'content_file_path': row['content_file_path'],
                        'csv_file': csv_file.name
                    })
        except Exception as e:
            print(f"Error leyendo {csv_file}: {e}")
    
    return csv_references

def validate_content_coverage(content_files, csv_references):
    """
    Valida la cobertura de archivos de contenido en los CSV
    """
    print("=== VALIDACIÓN DE ARCHIVOS DE CONTENIDO ===")
    print(f"Archivos de contenido encontrados: {len(content_files)}")
    print(f"Referencias en CSV: {len(csv_references)}")
    print()
    
    # Crear sets para comparación rápida
    content_files_set = {(cf['roadmap'], cf['node_id']) for cf in content_files}
    csv_references_set = {(cr['roadmap'], cr['node_id']) for cr in csv_references}
    
    # Archivos de contenido no referenciados en CSV
    missing_in_csv = content_files_set - csv_references_set
    
    # Referencias en CSV que no tienen archivo de contenido
    missing_content_files = csv_references_set - content_files_set
    
    print("📊 RESUMEN DE VALIDACIÓN:")
    print(f"✅ Archivos correctamente referenciados: {len(content_files_set & csv_references_set)}")
    print(f"❌ Archivos de contenido no referenciados en CSV: {len(missing_in_csv)}")
    print(f"⚠️  Referencias en CSV sin archivo de contenido: {len(missing_content_files)}")
    print()
    
    # Detalles de archivos no referenciados
    if missing_in_csv:
        print("🔍 ARCHIVOS DE CONTENIDO NO REFERENCIADOS EN CSV:")
        missing_files = [cf for cf in content_files if (cf['roadmap'], cf['node_id']) in missing_in_csv]
        for file_info in sorted(missing_files, key=lambda x: (x['roadmap'], x['filename'])):
            print(f"  📄 {file_info['roadmap']}: {file_info['filename']} (ID: {file_info['node_id']})")
            print(f"      Ruta: {file_info['relative_path']}")
        print()
    
    # Detalles de referencias sin archivo
    if missing_content_files:
        print("🔍 REFERENCIAS EN CSV SIN ARCHIVO DE CONTENIDO:")
        missing_refs = [cr for cr in csv_references if (cr['roadmap'], cr['node_id']) in missing_content_files]
        for ref_info in sorted(missing_refs, key=lambda x: (x['roadmap'], x['node_label'])):
            print(f"  📋 {ref_info['roadmap']}: {ref_info['node_label']} (ID: {ref_info['node_id']})")
            print(f"      CSV: {ref_info['csv_file']}")
            print(f"      Ruta esperada: {ref_info['content_file_path']}")
        print()
    
    # Verificar rutas de archivos
    print("🔍 VERIFICACIÓN DE RUTAS DE ARCHIVOS:")
    invalid_paths = []
    for ref in csv_references:
        file_path = Path(ref['content_file_path'])
        if not file_path.exists():
            invalid_paths.append(ref)
    
    if invalid_paths:
        print(f"❌ Rutas inválidas encontradas: {len(invalid_paths)}")
        for ref in invalid_paths[:10]:  # Mostrar solo los primeros 10
            print(f"  📋 {ref['roadmap']}: {ref['node_label']}")
            print(f"      Ruta: {ref['content_file_path']}")
        if len(invalid_paths) > 10:
            print(f"  ... y {len(invalid_paths) - 10} más")
    else:
        print("✅ Todas las rutas en CSV son válidas")
    
    print()
    
    # Estadísticas por roadmap
    print("📈 ESTADÍSTICAS POR ROADMAP:")
    roadmap_stats = {}
    
    # Contar archivos de contenido por roadmap
    for cf in content_files:
        roadmap = cf['roadmap']
        if roadmap not in roadmap_stats:
            roadmap_stats[roadmap] = {'content_files': 0, 'csv_references': 0}
        roadmap_stats[roadmap]['content_files'] += 1
    
    # Contar referencias en CSV por roadmap
    for cr in csv_references:
        roadmap = cr['roadmap']
        if roadmap not in roadmap_stats:
            roadmap_stats[roadmap] = {'content_files': 0, 'csv_references': 0}
        roadmap_stats[roadmap]['csv_references'] += 1
    
    for roadmap in sorted(roadmap_stats.keys()):
        stats = roadmap_stats[roadmap]
        content_count = stats['content_files']
        csv_count = stats['csv_references']
        coverage = (csv_count / content_count * 100) if content_count > 0 else 0
        
        status = "✅" if content_count == csv_count else "⚠️" if csv_count > 0 else "❌"
        print(f"  {status} {roadmap}: {csv_count}/{content_count} archivos ({coverage:.1f}% cobertura)")
    
    return {
        'total_content_files': len(content_files),
        'total_csv_references': len(csv_references),
        'correctly_referenced': len(content_files_set & csv_references_set),
        'missing_in_csv': len(missing_in_csv),
        'missing_content_files': len(missing_content_files),
        'invalid_paths': len(invalid_paths),
        'roadmap_stats': roadmap_stats
    }

def main():
    """
    Función principal de validación
    """
    # Usar rutas relativas al directorio padre desde InterviewTemplates
    base_dir = Path(__file__).parent.parent
    roadmaps_dir = base_dir / 'src' / 'data' / 'roadmaps'
    csv_dir = Path(__file__).parent / 'csv_output'
    
    print("🔍 Iniciando validación de archivos de contenido...\n")
    
    # Encontrar todos los archivos de contenido
    print("📂 Buscando archivos de contenido...")
    content_files = find_all_content_files(roadmaps_dir)
    
    # Cargar referencias desde CSV
    print("📊 Cargando referencias desde archivos CSV...")
    csv_references = load_csv_content_references(csv_dir)
    
    # Realizar validación
    validation_results = validate_content_coverage(content_files, csv_references)
    
    # Resumen final
    print("\n" + "="*50)
    print("📋 RESUMEN FINAL:")
    
    total_files = validation_results['total_content_files']
    total_refs = validation_results['total_csv_references']
    correctly_ref = validation_results['correctly_referenced']
    
    if total_files == total_refs == correctly_ref:
        print("🎉 ¡VALIDACIÓN EXITOSA! Todos los archivos están correctamente referenciados.")
    else:
        print(f"⚠️  Se encontraron inconsistencias:")
        print(f"   - Archivos de contenido: {total_files}")
        print(f"   - Referencias en CSV: {total_refs}")
        print(f"   - Correctamente referenciados: {correctly_ref}")
        
        if validation_results['missing_in_csv'] > 0:
            print(f"   - Archivos no referenciados: {validation_results['missing_in_csv']}")
        
        if validation_results['missing_content_files'] > 0:
            print(f"   - Referencias sin archivo: {validation_results['missing_content_files']}")
        
        if validation_results['invalid_paths'] > 0:
            print(f"   - Rutas inválidas: {validation_results['invalid_paths']}")

if __name__ == '__main__':
    main()