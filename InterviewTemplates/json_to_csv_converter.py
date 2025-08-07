#!/usr/bin/env python3
"""
Script para convertir archivos JSON de roadmaps a tablas CSV
"""

import json
import csv
import os
from pathlib import Path
import pandas as pd

def read_json_files(roadmaps_dir):
    """
    Lee todos los archivos JSON de las carpetas dentro de roadmaps
    """
    roadmaps_path = Path(roadmaps_dir)
    json_files = []
    
    # Buscar archivos JSON en cada subcarpeta
    for folder in roadmaps_path.iterdir():
        if folder.is_dir():
            # Buscar archivos JSON en la carpeta
            for json_file in folder.glob('*.json'):
                json_files.append({
                    'roadmap': folder.name,
                    'file_path': json_file,
                    'file_name': json_file.name
                })
    
    return json_files

def extract_node_data(json_data, roadmap_name):
    """
    Extrae datos de los nodos del JSON y establece relaciones padre-hijo
    """
    nodes_data = []
    
    # Función para buscar archivo de contenido basado en el ID del nodo
    def find_content_file(node_id, roadmap_name):
        if not node_id:
            return ''
        
        # Usar ruta absoluta desde el directorio base del proyecto
        base_dir = Path(__file__).parent.parent
        content_dir = base_dir / 'src' / 'data' / 'roadmaps' / roadmap_name / 'content'
        if not content_dir.exists():
            return ''
        
        # Buscar archivos que terminen con @{node_id}.md
        pattern = f'*@{node_id}.md'
        matching_files = list(content_dir.glob(pattern))
        
        if matching_files:
            # Retornar el path relativo desde la raíz del proyecto
            return str(matching_files[0])
        
        return ''
    
    # Crear un diccionario para mapear IDs a nodos para búsqueda rápida
    nodes_dict = {}
    if 'nodes' in json_data:
        for node in json_data['nodes']:
            nodes_dict[node.get('id', '')] = node
    
    # Crear un diccionario para mapear hijos a padres basado en edges
    child_to_parent = {}
    if 'edges' in json_data:
        for edge in json_data['edges']:
            source_id = edge.get('source', '')
            target_id = edge.get('target', '')
            if source_id and target_id:
                # El source es el padre, el target es el hijo
                child_to_parent[target_id] = source_id
    
    if 'nodes' in json_data:
        for node in json_data['nodes']:
            node_id = node.get('id', '')
            
            # Obtener información del nodo padre
            parent_id = child_to_parent.get(node_id, '')
            parent_label = ''
            if parent_id and parent_id in nodes_dict:
                parent_node = nodes_dict[parent_id]
                parent_label = parent_node.get('data', {}).get('label', '')
            
            # Buscar archivo de contenido correspondiente
            content_file_path = find_content_file(node_id, roadmap_name)
            
            node_info = {
                'roadmap': roadmap_name,
                'id': node_id,
                'type': node.get('type', ''),
                'position_x': node.get('position', {}).get('x', ''),
                'position_y': node.get('position', {}).get('y', ''),
                'width': node.get('width', ''),
                'height': node.get('height', ''),
                'label': node.get('data', {}).get('label', ''),
                'parent_id': parent_id,
                'parent_label': parent_label,
                'content_file_path': content_file_path,
                'selected': node.get('selected', False),
                'dragging': node.get('dragging', False),
                'zIndex': node.get('zIndex', '')
            }
            
            # Extraer estilos si existen
            if 'data' in node and 'style' in node['data']:
                style = node['data']['style']
                node_info.update({
                    'fontSize': style.get('fontSize', ''),
                    'backgroundColor': style.get('backgroundColor', ''),
                    'borderColor': style.get('borderColor', ''),
                    'stroke': style.get('stroke', ''),
                    'strokeWidth': style.get('strokeWidth', ''),
                    'textAlign': style.get('textAlign', '')
                })
            
            nodes_data.append(node_info)
    
    return nodes_data

def process_roadmaps(roadmaps_dir, output_dir='csv_output'):
    """
    Procesa todos los roadmaps y genera archivos CSV
    """
    # Crear directorio de salida
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Obtener todos los archivos JSON
    json_files = read_json_files(roadmaps_dir)
    
    all_nodes_data = []
    roadmap_summary = []
    
    print(f"Encontrados {len(json_files)} archivos JSON")
    
    for file_info in json_files:
        try:
            print(f"Procesando: {file_info['roadmap']}/{file_info['file_name']}")
            
            # Leer archivo JSON
            with open(file_info['file_path'], 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Extraer datos de nodos
            nodes_data = extract_node_data(json_data, file_info['roadmap'])
            all_nodes_data.extend(nodes_data)
            
            # Crear CSV individual para cada roadmap
            if nodes_data:
                df = pd.DataFrame(nodes_data)
                csv_filename = f"{file_info['roadmap']}_nodes.csv"
                csv_path = output_path / csv_filename
                df.to_csv(csv_path, index=False, encoding='utf-8')
                print(f"  -> Generado: {csv_filename} ({len(nodes_data)} nodos)")
            
            # Agregar al resumen
            roadmap_summary.append({
                'roadmap': file_info['roadmap'],
                'file_name': file_info['file_name'],
                'total_nodes': len(nodes_data),
                'node_types': len(set(node['type'] for node in nodes_data if node['type']))
            })
            
        except Exception as e:
            print(f"Error procesando {file_info['file_path']}: {e}")
    
    # Generar CSV consolidado con todos los nodos
    if all_nodes_data:
        df_all = pd.DataFrame(all_nodes_data)
        all_csv_path = output_path / 'all_roadmaps_nodes.csv'
        df_all.to_csv(all_csv_path, index=False, encoding='utf-8')
        print(f"\nGenerado archivo consolidado: all_roadmaps_nodes.csv ({len(all_nodes_data)} nodos totales)")
    
    # Generar resumen de roadmaps
    if roadmap_summary:
        df_summary = pd.DataFrame(roadmap_summary)
        summary_csv_path = output_path / 'roadmaps_summary.csv'
        df_summary.to_csv(summary_csv_path, index=False, encoding='utf-8')
        print(f"Generado resumen: roadmaps_summary.csv")
    
    return len(json_files), len(all_nodes_data)

def main():
    # Directorio de roadmaps (relativo al directorio padre)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roadmaps_dir = os.path.join(base_dir, 'src', 'data', 'roadmaps')
    csv_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv_output')
    
    if not os.path.exists(roadmaps_dir):
        print(f"Error: No se encontró el directorio {roadmaps_dir}")
        return
    
    print("Iniciando conversión de JSON a CSV...")
    print(f"Directorio de entrada: {roadmaps_dir}")
    print(f"Directorio de salida: csv_output")
    print("-" * 50)
    
    total_files, total_nodes = process_roadmaps(roadmaps_dir, csv_output_dir)
    
    print("-" * 50)
    print(f"Proceso completado:")
    print(f"  - Archivos procesados: {total_files}")
    print(f"  - Nodos totales extraídos: {total_nodes}")
    print(f"  - Archivos CSV generados en: csv_output/")

if __name__ == '__main__':
    main()