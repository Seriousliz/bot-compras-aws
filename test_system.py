#!/usr/bin/env python3
"""
Script de pruebas completas del sistema Bot de Compras
"""
import requests
import json
import time

# Configuración
API_ENDPOINT = "https://2tttwbrm34.execute-api.us-west-2.amazonaws.com/prod"

def test_health_check():
    """Probar endpoint de health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{API_ENDPOINT}/health")
        if response.status_code == 200:
            print("✅ Health check exitoso:", response.json())
            return True
        else:
            print("❌ Health check falló:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error en health check:", e)
        return False

def test_chat_compra():
    """Probar consulta de compra"""
    print("\n🛒 Probando consulta de compra...")
    try:
        payload = {
            "message": "Quiero comprar una lavadora económica",
            "user_email": "test@example.com"
        }
        
        response = requests.post(
            f"{API_ENDPOINT}/chat",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Consulta de compra exitosa")
            print(f"   Respuesta: {data['respuesta'][:100]}...")
            print(f"   Productos encontrados: {len(data['productos'])}")
            print(f"   Intención detectada: {data['intencion']}")
            return True
        else:
            print("❌ Consulta de compra falló:", response.status_code, response.text)
            return False
    except Exception as e:
        print("❌ Error en consulta de compra:", e)
        return False

def test_chat_soporte():
    """Probar consulta de soporte"""
    print("\n🔧 Probando consulta de soporte...")
    try:
        payload = {
            "message": "Mi refrigerador no enfría bien, tiene un problema",
            "user_email": "test@example.com"
        }
        
        response = requests.post(
            f"{API_ENDPOINT}/chat",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Consulta de soporte exitosa")
            print(f"   Respuesta: {data['respuesta']}")
            print(f"   Intención detectada: {data['intencion']}")
            
            # Verificar que redirige correctamente
            if "solo para asistencia de compras" in data['respuesta']:
                print("✅ Redirección de soporte correcta")
                return True
            else:
                print("❌ No redirigió correctamente el soporte")
                return False
        else:
            print("❌ Consulta de soporte falló:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error en consulta de soporte:", e)
        return False

def test_multiple_users():
    """Probar múltiples usuarios"""
    print("\n👥 Probando múltiples usuarios...")
    users = ["user1@test.com", "user2@test.com", "user3@test.com"]
    success_count = 0
    
    for user in users:
        try:
            payload = {
                "message": f"Hola, soy {user} y busco electrodomésticos",
                "user_email": user
            }
            
            response = requests.post(
                f"{API_ENDPOINT}/chat",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Usuario {user} procesado correctamente")
            else:
                print(f"❌ Usuario {user} falló: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con usuario {user}: {e}")
    
    print(f"📊 Resultado: {success_count}/{len(users)} usuarios exitosos")
    return success_count == len(users)

def test_performance():
    """Probar rendimiento básico"""
    print("\n⚡ Probando rendimiento...")
    times = []
    
    for i in range(5):
        start_time = time.time()
        
        payload = {
            "message": f"Consulta de rendimiento #{i+1}",
            "user_email": "performance@test.com"
        }
        
        try:
            response = requests.post(
                f"{API_ENDPOINT}/chat",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            times.append(response_time)
            
            if response.status_code == 200:
                print(f"✅ Consulta #{i+1}: {response_time:.2f}s")
            else:
                print(f"❌ Consulta #{i+1} falló: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en consulta #{i+1}: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        print(f"📊 Tiempo promedio: {avg_time:.2f}s")
        print(f"📊 Tiempo máximo: {max_time:.2f}s")
        
        # Verificar SLA (< 3 segundos)
        if avg_time < 3.0:
            print("✅ Rendimiento dentro del SLA (<3s)")
            return True
        else:
            print("❌ Rendimiento fuera del SLA")
            return False
    
    return False

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas completas del sistema Bot de Compras")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Chat Compra", test_chat_compra),
        ("Chat Soporte", test_chat_soporte),
        ("Múltiples Usuarios", test_multiple_users),
        ("Rendimiento", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        result = test_func()
        results.append((test_name, result))
        
        if result:
            print(f"✅ {test_name}: PASÓ")
        else:
            print(f"❌ {test_name}: FALLÓ")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:20} {status}")
    
    print(f"\n🎯 Resultado final: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar los errores anteriores.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
