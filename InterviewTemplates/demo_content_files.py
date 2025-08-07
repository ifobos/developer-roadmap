#!/usr/bin/env python3
"""
Script de demostración para mostrar la relación entre nodos y archivos de contenido
"""

import pandas as pd
import os
from pathlib import Path

def analyze_content_coverage():
    """
    Analiza la cobertura de archivos de contenido en los roadmaps
    """
    print("=" * 60)
    print("ANÁLISIS DE COBERTURA DE ARCHIVOS DE CONTENIDO")
    print("=" * 60)
    
    # Configurar ruta base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Cargar datos
    df = pd.read_csv(os.path.join(base_dir, 'csv_output', 'all_roadmaps_nodes.csv'))
    
    # Análisis general
    total_nodos = len(df)
    nodos_con_contenido = df[df['content_file_path'].notna() & (df['content_file_path'] != '')]
    total_con_contenido = len(nodos_con_contenido)
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Total de nodos: {total_nodos:,}")
    print(f"   • Nodos con archivo de contenido: {total_con_contenido:,}")
    print(f"   • Porcentaje de cobertura: {total_con_contenido/total_nodos*100:.1f}%")
    print()
    
    # Análisis por roadmap
    print(f"📈 COBERTURA POR ROADMAP:")
    roadmap_stats = []
    
    for roadmap in df['roadmap'].unique():
        roadmap_df = df[df['roadmap'] == roadmap]
        roadmap_total = len(roadmap_df)
        roadmap_con_contenido = len(roadmap_df[roadmap_df['content_file_path'].notna() & (roadmap_df['content_file_path'] != '')])
        cobertura = roadmap_con_contenido / roadmap_total * 100 if roadmap_total > 0 else 0
        
        roadmap_stats.append({
            'roadmap': roadmap,
            'total_nodos': roadmap_total,
            'con_contenido': roadmap_con_contenido,
            'cobertura': cobertura
        })
    
    # Ordenar por cobertura descendente
    roadmap_stats.sort(key=lambda x: x['cobertura'], reverse=True)
    
    print(f"   {'Roadmap':<25} {'Total':<8} {'Con contenido':<15} {'Cobertura':<10}")
    print(f"   {'-'*25} {'-'*8} {'-'*15} {'-'*10}")
    
    for stats in roadmap_stats[:15]:  # Top 15
        print(f"   {stats['roadmap']:<25} {stats['total_nodos']:<8} {stats['con_contenido']:<15} {stats['cobertura']:<10.1f}%")
    
    print(f"   ... y {len(roadmap_stats)-15} roadmaps más")
    print()
    
    return nodos_con_contenido

def show_content_examples(nodos_con_contenido):
    """
    Muestra ejemplos de la relación nodo-archivo
    """
    print("=" * 60)
    print("EJEMPLOS DE RELACIÓN NODO-ARCHIVO")
    print("=" * 60)
    
    # Ejemplos de diferentes roadmaps
    roadmaps_ejemplo = ['ios', 'react', 'nodejs', 'python', 'backend']
    
    for roadmap in roadmaps_ejemplo:
        roadmap_contenido = nodos_con_contenido[nodos_con_contenido['roadmap'] == roadmap]
        if len(roadmap_contenido) > 0:
            print(f"\n🗂️  ROADMAP: {roadmap.upper()}")
            
            # Mostrar algunos ejemplos
            ejemplos = roadmap_contenido.head(3)
            for _, row in ejemplos.iterrows():
                print(f"   📄 {row['label']:<30} -> {Path(row['content_file_path']).name}")
                
                # Verificar si el archivo existe y mostrar primeras líneas
                if os.path.exists(row['content_file_path']):
                    try:
                        with open(row['content_file_path'], 'r', encoding='utf-8') as f:
                            primera_linea = f.readline().strip()
                            if primera_linea.startswith('#'):
                                print(f"      └─ {primera_linea}")
                    except Exception as e:
                        print(f"      └─ Error leyendo archivo: {e}")
                else:
                    print(f"      └─ ⚠️  Archivo no encontrado")

def analyze_content_types(nodos_con_contenido):
    """
    Analiza los tipos de nodos que tienen contenido
    """
    print("\n" + "=" * 60)
    print("ANÁLISIS POR TIPO DE NODO")
    print("=" * 60)
    
    # Análisis por tipo
    tipo_stats = nodos_con_contenido['type'].value_counts()
    
    print(f"📊 DISTRIBUCIÓN POR TIPO DE NODO:")
    for tipo, cantidad in tipo_stats.items():
        print(f"   • {tipo:<15}: {cantidad:>4} nodos")
    
    print()
    
    # Ejemplos por tipo
    print(f"🔍 EJEMPLOS POR TIPO:")
    for tipo in ['topic', 'subtopic', 'section']:
        if tipo in tipo_stats.index:
            ejemplos = nodos_con_contenido[nodos_con_contenido['type'] == tipo]['label'].head(3).tolist()
            print(f"   • {tipo}: {', '.join(ejemplos)}")

def find_missing_content():
    """
    Identifica nodos que podrían tener contenido pero no lo tienen
    """
    print("\n" + "=" * 60)
    print("NODOS SIN ARCHIVO DE CONTENIDO")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_dir, 'csv_output', 'all_roadmaps_nodes.csv'))
    
    # Filtrar nodos que probablemente deberían tener contenido
    nodos_sin_contenido = df[
        (df['content_file_path'].isna() | (df['content_file_path'] == '')) &
        (df['type'].isin(['topic', 'subtopic'])) &
        (df['label'].notna()) &
        (df['label'] != '')
    ]
    
    print(f"📋 ESTADÍSTICAS:")
    print(f"   • Total nodos sin contenido: {len(nodos_sin_contenido):,}")
    print(f"   • Tipos: {nodos_sin_contenido['type'].value_counts().to_dict()}")
    
    # Mostrar algunos ejemplos por roadmap
    print(f"\n🔍 EJEMPLOS DE NODOS SIN CONTENIDO:")
    for roadmap in ['ios', 'react', 'nodejs']:
        roadmap_sin_contenido = nodos_sin_contenido[nodos_sin_contenido['roadmap'] == roadmap]
        if len(roadmap_sin_contenido) > 0:
            print(f"\n   📱 {roadmap.upper()}:")
            ejemplos = roadmap_sin_contenido['label'].head(5).tolist()
            for ejemplo in ejemplos:
                print(f"      • {ejemplo}")

def main():
    """
    Función principal que ejecuta todos los análisis
    """
    print("🔍 ANÁLISIS DE ARCHIVOS DE CONTENIDO EN ROADMAPS")
    print("Este script analiza la relación entre nodos y archivos de contenido\n")
    
    try:
        # Configurar ruta base
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(base_dir, 'csv_output', 'all_roadmaps_nodes.csv')
        
        # Verificar que existe el archivo CSV
        if not os.path.exists(csv_file):
            print("❌ Error: No se encontró el archivo csv_output/all_roadmaps_nodes.csv")
            print("   Ejecuta primero: python json_to_csv_converter.py")
            return
        
        # Ejecutar análisis
        nodos_con_contenido = analyze_content_coverage()
        show_content_examples(nodos_con_contenido)
        analyze_content_types(nodos_con_contenido)
        find_missing_content()
        
        print("\n" + "=" * 60)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 60)
        print("💡 Usa estos datos para:")
        print("   • Identificar gaps en la documentación")
        print("   • Priorizar creación de contenido")
        print("   • Analizar la completitud de los roadmaps")
        print("   • Crear herramientas de navegación")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()