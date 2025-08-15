#!/usr/bin/env python3
"""
Script de demostración para mostrar las relaciones jerárquicas
"""

import pandas as pd
import os

def demo_hierarchy_analysis():
    """
    Demostración del análisis de jerarquías
    """
    print("DEMOSTRACIÓN: Análisis de Relaciones Jerárquicas en Roadmaps")
    print("=" * 65)
    
    # Configurar ruta base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Analizar el roadmap de iOS como ejemplo
    ios_file = os.path.join(base_dir, 'csv_output', 'ios_nodes.csv')
    if os.path.exists(ios_file):
        df = pd.read_csv(ios_file)
        
        print(f"\n📱 ROADMAP: iOS Developer")
        print(f"Total de nodos: {len(df)}")
        
        # Nodos raíz vs nodos con padre
        root_nodes = df[df['parent_id'].isna() | (df['parent_id'] == '')]
        child_nodes = df[df['parent_id'].notna() & (df['parent_id'] != '')]
        
        print(f"Nodos raíz (sin padre): {len(root_nodes)}")
        print(f"Nodos con padre: {len(child_nodes)}")
        print(f"Porcentaje con jerarquía: {len(child_nodes)/len(df)*100:.1f}%")
        
        # Mostrar ejemplos de relaciones
        print("\n🔗 Ejemplos de relaciones padre → hijo:")
        examples = child_nodes[child_nodes['parent_label'] != ''].head(8)
        for _, row in examples.iterrows():
            print(f"  • {row['parent_label']} → {row['label']}")
        
        # Análisis por tipo
        print("\n📊 Distribución por tipo de nodo:")
        type_counts = df['type'].value_counts()
        for node_type, count in type_counts.items():
            print(f"  • {node_type}: {count}")
        
        # Nodos con más hijos
        print("\n👥 Top 5 nodos con más hijos:")
        parent_counts = child_nodes['parent_id'].value_counts().head(5)
        for parent_id, child_count in parent_counts.items():
            parent_info = df[df['id'] == parent_id]
            if len(parent_info) > 0:
                parent_label = parent_info['label'].iloc[0]
                parent_type = parent_info['type'].iloc[0]
                print(f"  • {parent_label} ({parent_type}): {child_count} hijos")
    
    # Resumen de todos los roadmaps
    print("\n" + "=" * 65)
    print("📈 RESUMEN DE TODOS LOS ROADMAPS")
    print("=" * 65)
    
    csv_dir = os.path.join(base_dir, 'csv_output')
    results = []
    
    for filename in os.listdir(csv_dir):
        if filename.endswith('_nodes.csv') and filename != 'all_roadmaps_nodes.csv':
            try:
                df = pd.read_csv(os.path.join(csv_dir, filename))
                roadmap_name = df['roadmap'].iloc[0] if len(df) > 0 else filename.replace('_nodes.csv', '')
                
                root_nodes = df[df['parent_id'].isna() | (df['parent_id'] == '')]
                child_nodes = df[df['parent_id'].notna() & (df['parent_id'] != '')]
                hierarchy_ratio = len(child_nodes) / len(df) * 100 if len(df) > 0 else 0
                
                results.append({
                    'roadmap': roadmap_name,
                    'total_nodes': len(df),
                    'hierarchy_ratio': hierarchy_ratio
                })
            except Exception as e:
                continue
    
    # Ordenar por número de nodos
    results.sort(key=lambda x: x['total_nodes'], reverse=True)
    
    print(f"\nTotal de roadmaps analizados: {len(results)}")
    print(f"Total de nodos: {sum(r['total_nodes'] for r in results)}")
    
    print("\n🏆 Top 10 roadmaps con más nodos:")
    for i, result in enumerate(results[:10], 1):
        print(f"  {i:2d}. {result['roadmap']:<25} {result['total_nodes']:>4} nodos ({result['hierarchy_ratio']:>5.1f}% jerárquicos)")
    
    print("\n🌳 Top 10 roadmaps con mayor estructura jerárquica:")
    hierarchy_sorted = sorted(results, key=lambda x: x['hierarchy_ratio'], reverse=True)
    for i, result in enumerate(hierarchy_sorted[:10], 1):
        if result['hierarchy_ratio'] > 0:
            print(f"  {i:2d}. {result['roadmap']:<25} {result['hierarchy_ratio']:>5.1f}% nodos con padre")
    
    print("\n✅ Análisis completado. Los archivos CSV ahora incluyen:")
    print("   • parent_id: ID del nodo padre")
    print("   • parent_label: Nombre del nodo padre")
    print("   • Relaciones jerárquicas completas para análisis avanzado")

if __name__ == '__main__':
    demo_hierarchy_analysis()