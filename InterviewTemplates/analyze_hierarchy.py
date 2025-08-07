#!/usr/bin/env python3
"""
Script de ejemplo para analizar las relaciones jerárquicas en los roadmaps
"""

import pandas as pd
import os
from collections import defaultdict

def analyze_roadmap_hierarchy(csv_file):
    """
    Analiza la jerarquía de un roadmap específico
    """
    if not os.path.exists(csv_file):
        print(f"Error: No se encontró el archivo {csv_file}")
        return
    
    df = pd.read_csv(csv_file)
    roadmap_name = df['roadmap'].iloc[0] if len(df) > 0 else "Unknown"
    
    print(f"\n=== ANÁLISIS DE JERARQUÍA: {roadmap_name.upper()} ===")
    print(f"Total de nodos: {len(df)}")
    
    # Nodos raíz (sin padre)
    root_nodes = df[df['parent_id'].isna() | (df['parent_id'] == '')]
    print(f"Nodos raíz (sin padre): {len(root_nodes)}")
    
    # Nodos con padre
    child_nodes = df[df['parent_id'].notna() & (df['parent_id'] != '')]
    print(f"Nodos con padre: {len(child_nodes)}")
    
    # Análisis por tipo de nodo
    print("\n--- Distribución por tipo ---")
    type_counts = df['type'].value_counts()
    for node_type, count in type_counts.items():
        print(f"  {node_type}: {count}")
    
    # Nodos más conectados (que más hijos tienen)
    print("\n--- Top 10 nodos con más hijos ---")
    parent_counts = child_nodes['parent_id'].value_counts().head(10)
    for parent_id, child_count in parent_counts.items():
        parent_info = df[df['id'] == parent_id]
        if len(parent_info) > 0:
            parent_label = parent_info['label'].iloc[0]
            parent_type = parent_info['type'].iloc[0]
            print(f"  {parent_label} ({parent_type}): {child_count} hijos")
    
    # Mostrar algunos ejemplos de jerarquía
    print("\n--- Ejemplos de relaciones padre-hijo ---")
    examples = child_nodes[child_nodes['parent_label'] != ''].head(5)
    for _, row in examples.iterrows():
        print(f"  {row['parent_label']} → {row['label']}")
    
    return {
        'roadmap': roadmap_name,
        'total_nodes': len(df),
        'root_nodes': len(root_nodes),
        'child_nodes': len(child_nodes),
        'node_types': len(type_counts)
    }

def analyze_all_roadmaps():
    """
    Analiza todos los roadmaps y genera un resumen comparativo
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(base_dir, 'csv_output')
    if not os.path.exists(csv_dir):
        print(f"Error: No se encontró el directorio {csv_dir}")
        return
    
    results = []
    
    # Analizar archivos individuales de roadmaps
    for filename in os.listdir(csv_dir):
        if filename.endswith('_nodes.csv') and filename != 'all_roadmaps_nodes.csv':
            csv_path = os.path.join(csv_dir, filename)
            result = analyze_roadmap_hierarchy(csv_path)
            if result:
                results.append(result)
    
    # Crear resumen comparativo
    if results:
        print("\n" + "="*60)
        print("RESUMEN COMPARATIVO DE TODOS LOS ROADMAPS")
        print("="*60)
        
        df_summary = pd.DataFrame(results)
        df_summary = df_summary.sort_values('total_nodes', ascending=False)
        
        print(f"\nTotal de roadmaps analizados: {len(df_summary)}")
        print(f"Total de nodos en todos los roadmaps: {df_summary['total_nodes'].sum()}")
        print(f"Promedio de nodos por roadmap: {df_summary['total_nodes'].mean():.1f}")
        
        print("\n--- Top 10 roadmaps con más nodos ---")
        top_roadmaps = df_summary.head(10)
        for _, row in top_roadmaps.iterrows():
            hierarchy_ratio = (row['child_nodes'] / row['total_nodes'] * 100) if row['total_nodes'] > 0 else 0
            print(f"  {row['roadmap']}: {row['total_nodes']} nodos ({hierarchy_ratio:.1f}% con jerarquía)")
        
        print("\n--- Roadmaps con mayor estructura jerárquica ---")
        df_summary['hierarchy_ratio'] = (df_summary['child_nodes'] / df_summary['total_nodes'] * 100).fillna(0)
        top_hierarchy = df_summary.sort_values('hierarchy_ratio', ascending=False).head(10)
        for _, row in top_hierarchy.iterrows():
            print(f"  {row['roadmap']}: {row['hierarchy_ratio']:.1f}% nodos con padre")

def find_learning_paths(roadmap_name):
    """
    Encuentra rutas de aprendizaje en un roadmap específico
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, 'csv_output', f'{roadmap_name}_nodes.csv')
    if not os.path.exists(csv_file):
        print(f"Error: No se encontró el archivo {csv_file}")
        return
    
    df = pd.read_csv(csv_file)
    
    print(f"\n=== RUTAS DE APRENDIZAJE: {roadmap_name.upper()} ===")
    
    # Construir árbol de dependencias
    children_map = defaultdict(list)
    for _, row in df.iterrows():
        if pd.notna(row['parent_id']) and row['parent_id'] != '':
            children_map[row['parent_id']].append({
                'id': row['id'],
                'label': row['label'],
                'type': row['type']
            })
    
    # Encontrar nodos raíz
    root_nodes = df[df['parent_id'].isna() | (df['parent_id'] == '')]
    
    def print_tree(node_id, node_label, level=0, max_level=3):
        if level > max_level:
            return
        
        indent = "  " * level
        print(f"{indent}{'└─' if level > 0 else ''} {node_label}")
        
        if node_id in children_map:
            for child in children_map[node_id][:3]:  # Limitar a 3 hijos por nodo
                print_tree(child['id'], child['label'], level + 1, max_level)
    
    # Mostrar algunas rutas de aprendizaje
    print("\n--- Rutas de aprendizaje principales ---")
    topic_roots = root_nodes[root_nodes['type'].isin(['topic', 'title'])].head(5)
    
    for _, root in topic_roots.iterrows():
        if pd.notna(root['label']) and root['label'].strip():
            print_tree(root['id'], root['label'])
            print()

def main():
    print("Analizador de Jerarquías de Roadmaps")
    print("=====================================")
    
    while True:
        print("\nOpciones:")
        print("1. Analizar todos los roadmaps")
        print("2. Analizar un roadmap específico")
        print("3. Mostrar rutas de aprendizaje")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == '1':
            analyze_all_roadmaps()
        
        elif choice == '2':
            roadmap = input("Nombre del roadmap (ej: ios, react, python): ").strip()
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file = os.path.join(base_dir, 'csv_output', f'{roadmap}_nodes.csv')
            analyze_roadmap_hierarchy(csv_file)
        
        elif choice == '3':
            roadmap = input("Nombre del roadmap (ej: ios, react, python): ").strip()
            find_learning_paths(roadmap)
        
        elif choice == '4':
            print("¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Por favor, selecciona 1-4.")

if __name__ == '__main__':
    main()