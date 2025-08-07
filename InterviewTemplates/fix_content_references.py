#!/usr/bin/env python3
"""
Script para corregir las referencias de archivos de contenido en los CSV.
Identifica y corrige:
1. Duplicados en las referencias
2. Archivos de contenido no referenciados
3. Referencias inválidas
"""

import os
import pandas as pd
from pathlib import Path
import json
from collections import defaultdict

def find_all_content_files(roadmaps_dir):
    """Encuentra todos los archivos de contenido .md"""
    content_files = []
    roadmaps_path = Path(roadmaps_dir)
    
    for roadmap_dir in roadmaps_path.iterdir():
        if roadmap_dir.is_dir():
            content_dir = roadmap_dir / 'content'
            if content_dir.exists():
                for md_file in content_dir.glob('*.md'):
                    filename = md_file.name
                    if '@' in filename:
                        parts = filename.split('@')
                        if len(parts) == 2:
                            node_id = parts[1].replace('.md', '')
                            content_files.append({
                                'roadmap': roadmap_dir.name,
                                'file_path': str(md_file),
                                'node_id': node_id,
                                'filename': filename,
                                'content_name': parts[0]
                            })
    
    return content_files

def load_json_nodes(roadmaps_dir):
    """Carga todos los nodos desde los archivos JSON"""
    json_nodes = {}
    roadmaps_path = Path(roadmaps_dir)
    
    for roadmap_dir in roadmaps_path.iterdir():
        if roadmap_dir.is_dir():
            json_file = roadmap_dir / f'{roadmap_dir.name}.json'
            if json_file.exists():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        nodes = data.get('nodes', [])
                        json_nodes[roadmap_dir.name] = {node['id']: node for node in nodes}
                except Exception as e:
                    print(f"❌ Error cargando {json_file}: {e}")
    
    return json_nodes

def fix_csv_references(csv_output_dir, content_files, json_nodes):
    """Corrige las referencias en los archivos CSV"""
    csv_dir = Path(csv_output_dir)
    
    # Crear índice de archivos de contenido por roadmap y node_id
    content_index = defaultdict(dict)
    for content in content_files:
        content_index[content['roadmap']][content['node_id']] = content
    
    fixes_summary = {
        'files_processed': 0,
        'duplicates_removed': 0,
        'missing_references_added': 0,
        'invalid_references_removed': 0
    }
    
    # Debug: listar archivos encontrados
    csv_files = list(csv_dir.glob('*_nodes.csv'))
    print(f"\n🔍 Archivos CSV encontrados: {len(csv_files)}")
    for f in csv_files[:5]:  # Mostrar solo los primeros 5
        print(f"  - {f.name}")
    
    for csv_file in csv_files:
        if csv_file.name == 'all_roadmaps_nodes.csv' or csv_file.name == 'roadmaps_summary.csv':
            continue  # Saltar archivos de resumen
        roadmap_name = csv_file.stem.replace('_nodes', '')
        print(f"\n🔧 Procesando {csv_file.name}...")
        
        try:
            # Cargar CSV
            df = pd.read_csv(csv_file)
            original_count = len(df)
            
            # Verificar qué columna usar para el ID del nodo
            id_column = 'id' if 'id' in df.columns else 'node_id'
            
            # Eliminar duplicados basados en el ID del nodo
            df_deduplicated = df.drop_duplicates(subset=[id_column], keep='first')
            duplicates_removed = original_count - len(df_deduplicated)
            
            if duplicates_removed > 0:
                print(f"  ✅ Eliminados {duplicates_removed} duplicados")
                fixes_summary['duplicates_removed'] += duplicates_removed
            
            # Corregir referencias de contenido
            missing_added = 0
            invalid_removed = 0
            
            for idx, row in df_deduplicated.iterrows():
                node_id = row[id_column]
                current_content_path = row.get('content_file_path', '')
                
                # Verificar si existe contenido para este nodo
                if node_id in content_index[roadmap_name]:
                    content_info = content_index[roadmap_name][node_id]
                    expected_path = f"src/data/roadmaps/{roadmap_name}/content/{content_info['filename']}"
                    
                    if pd.isna(current_content_path) or current_content_path == '':
                        # Agregar referencia faltante
                        df_deduplicated.at[idx, 'content_file_path'] = expected_path
                        missing_added += 1
                    elif current_content_path != expected_path:
                        # Corregir referencia incorrecta
                        df_deduplicated.at[idx, 'content_file_path'] = expected_path
                        invalid_removed += 1
                else:
                    # No hay contenido para este nodo, limpiar referencia
                    if not pd.isna(current_content_path) and current_content_path != '':
                        df_deduplicated.at[idx, 'content_file_path'] = ''
                        invalid_removed += 1
            
            if missing_added > 0:
                print(f"  ✅ Agregadas {missing_added} referencias faltantes")
                fixes_summary['missing_references_added'] += missing_added
            
            if invalid_removed > 0:
                print(f"  ✅ Corregidas {invalid_removed} referencias inválidas")
                fixes_summary['invalid_references_removed'] += invalid_removed
            
            # Guardar CSV corregido
            df_deduplicated.to_csv(csv_file, index=False)
            fixes_summary['files_processed'] += 1
            
        except Exception as e:
            print(f"  ❌ Error procesando {csv_file}: {e}")
    
    return fixes_summary

def generate_missing_content_report(content_files, json_nodes):
    """Genera reporte de archivos de contenido que no tienen nodos correspondientes"""
    print("\n📋 ARCHIVOS DE CONTENIDO SIN NODOS CORRESPONDIENTES:")
    
    orphaned_files = []
    
    for content in content_files:
        roadmap = content['roadmap']
        node_id = content['node_id']
        
        if roadmap in json_nodes:
            if node_id not in json_nodes[roadmap]:
                orphaned_files.append(content)
        else:
            orphaned_files.append(content)
    
    if orphaned_files:
        for content in orphaned_files[:20]:  # Mostrar solo los primeros 20
            print(f"  📄 {content['roadmap']}: {content['filename']} (ID: {content['node_id']})")
        
        if len(orphaned_files) > 20:
            print(f"  ... y {len(orphaned_files) - 20} archivos más")
    else:
        print("  ✅ Todos los archivos de contenido tienen nodos correspondientes")
    
    return orphaned_files

def main():
    # Configuración de rutas
    base_dir = Path(__file__).parent.parent
    roadmaps_dir = base_dir / 'src' / 'data' / 'roadmaps'
    csv_output_dir = Path(__file__).parent / 'csv_output'
    
    print("🔧 Iniciando corrección de referencias de contenido...")
    
    # Buscar archivos de contenido
    print("\n📂 Buscando archivos de contenido...")
    content_files = find_all_content_files(roadmaps_dir)
    print(f"Archivos de contenido encontrados: {len(content_files)}")
    
    # Cargar nodos desde JSON
    print("\n📊 Cargando nodos desde archivos JSON...")
    json_nodes = load_json_nodes(roadmaps_dir)
    total_nodes = sum(len(nodes) for nodes in json_nodes.values())
    print(f"Nodos cargados desde JSON: {total_nodes}")
    
    # Corregir referencias en CSV
    print("\n🔧 Corrigiendo referencias en archivos CSV...")
    fixes_summary = fix_csv_references(csv_output_dir, content_files, json_nodes)
    
    # Generar reporte de archivos huérfanos
    orphaned_files = generate_missing_content_report(content_files, json_nodes)
    
    # Resumen final
    print("\n" + "="*50)
    print("📋 RESUMEN DE CORRECCIONES:")
    print(f"✅ Archivos CSV procesados: {fixes_summary['files_processed']}")
    print(f"🔄 Duplicados eliminados: {fixes_summary['duplicates_removed']}")
    print(f"➕ Referencias faltantes agregadas: {fixes_summary['missing_references_added']}")
    print(f"🔧 Referencias inválidas corregidas: {fixes_summary['invalid_references_removed']}")
    print(f"📄 Archivos de contenido huérfanos: {len(orphaned_files)}")
    
    if fixes_summary['files_processed'] > 0:
        print("\n✅ Correcciones completadas. Ejecuta el script de validación nuevamente para verificar.")
    else:
        print("\n⚠️  No se procesaron archivos CSV.")

if __name__ == "__main__":
    main()