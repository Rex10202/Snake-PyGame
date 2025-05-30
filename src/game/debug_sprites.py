import pygame
import os

def verificar_sprites():
    """Función de diagnóstico para verificar la carga de sprites."""
    print("=== DIAGNÓSTICO DE SPRITES ===\n")
    
    # 1. Verificar la ruta base
    archivo_actual = __file__
    directorio_actual = os.path.dirname(archivo_actual)
    print(f"📁 Archivo actual: {archivo_actual}")
    print(f"📁 Directorio actual: {directorio_actual}")
    
    # 2. Verificar ruta de sprites
    ruta_sprites = os.path.join(directorio_actual, "assets", "sprites", "Serpiente")
    print(f"📁 Ruta de sprites: {ruta_sprites}")
    print(f"📁 ¿Existe la carpeta? {os.path.exists(ruta_sprites)}")
    
    if not os.path.exists(ruta_sprites):
        print("❌ ERROR: La carpeta de sprites no existe!")
        print("\n🔧 SOLUCIONES:")
        print("1. Crear la carpeta: assets/sprites/Serpiente/")
        print("2. Verificar que esté en el mismo directorio que main_menu.py")
        return False
    
    # 3. Verificar archivos específicos
    archivos_requeridos = {
        "Cabeza": ["Snake head1.png"],
        "Cuerpo": ["Body.png", "Tail.png"],
        "Cuerpo/Direcciones": ["BodyDR.png", "BodyLD.png", "BodyRU.png", "BodyUD.png"]
    }
    
    archivos_faltantes = []
    archivos_encontrados = []
    
    for carpeta, archivos in archivos_requeridos.items():
        ruta_carpeta = os.path.join(ruta_sprites, carpeta)
        print(f"\n📂 Verificando carpeta: {carpeta}")
        print(f"   Ruta: {ruta_carpeta}")
        print(f"   ¿Existe? {os.path.exists(ruta_carpeta)}")
        
        if os.path.exists(ruta_carpeta):
            contenido = os.listdir(ruta_carpeta)
            print(f"   Contenido: {contenido}")
            
            for archivo in archivos:
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                if os.path.exists(ruta_archivo):
                    print(f"   ✅ {archivo} - ENCONTRADO")
                    archivos_encontrados.append(f"{carpeta}/{archivo}")
                else:
                    print(f"   ❌ {archivo} - FALTANTE")
                    archivos_faltantes.append(f"{carpeta}/{archivo}")
        else:
            print(f"   ❌ Carpeta no existe")
            for archivo in archivos:
                archivos_faltantes.append(f"{carpeta}/{archivo}")
    
    # 4. Resumen
    print(f"\n📊 RESUMEN:")
    print(f"✅ Archivos encontrados: {len(archivos_encontrados)}")
    print(f"❌ Archivos faltantes: {len(archivos_faltantes)}")
    
    if archivos_faltantes:
        print(f"\n🚨 ARCHIVOS FALTANTES:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
    
    # 5. Verificar pygame
    try:
        pygame.init()
        print(f"\n🎮 Pygame inicializado correctamente")
        
        # Intentar cargar una imagen de prueba si existe
        if archivos_encontrados:
            primer_archivo = archivos_encontrados[0]
            carpeta, nombre = primer_archivo.split('/', 1)
            ruta_test = os.path.join(ruta_sprites, carpeta, nombre)
            try:
                imagen_test = pygame.image.load(ruta_test)
                print(f"✅ Prueba de carga exitosa: {primer_archivo}")
                print(f"   Tamaño: {imagen_test.get_size()}")
            except Exception as e:
                print(f"❌ Error al cargar {primer_archivo}: {e}")
    except Exception as e:
        print(f"❌ Error con pygame: {e}")
    
    return len(archivos_faltantes) == 0

if __name__ == "__main__":
    verificar_sprites()
