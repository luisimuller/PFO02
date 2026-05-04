import requests

BASE_URL = "http://127.0.0.1:8000"

def menu():
    print("\n╔════════════════════════════╗")
    print("║    📋 Gestor de Tareas     ║")
    print("╠════════════════════════════╣")
    print("║  1. Registrar usuario      ║")
    print("║  2. Iniciar sesión         ║")
    print("║  3. Ver página de tareas   ║")
    print("║  0. Salir                  ║")
    print("╚════════════════════════════╝")
    return input("Opción: ").strip()

def registrar():
    print("\n── Registro de usuario ──")
    usuario = input("Nombre de usuario: ").strip()
    contrasena = input("Contrasena: ").strip()
    resp = requests.post(f"{BASE_URL}/registro", json={"usuario": usuario, "contrasena": contrasena})
    print(f"→ [{resp.status_code}] {resp.json()}")

def iniciar_sesion():
    print("\n── Inicio de sesion ──")
    usuario = input("Nombre de usuario: ").strip()
    contrasena = input("Contrasena: ").strip()
    resp = requests.post(f"{BASE_URL}/login", json={"usuario": usuario, "contrasena": contrasena})
    print(f"→ [{resp.status_code}] {resp.json()}")

def ver_tareas():
    resp = requests.get(f"{BASE_URL}/tareas")
    print(f"\n→ [{resp.status_code}] La página HTML fue recibida correctamente.")
    print("   Abrí http://127.0.0.1:8000/tareas en tu navegador para verla.")

def main():
    print("\nConectando al servidor en", BASE_URL)
    while True:
        opcion = menu()
        if opcion == "1":
            registrar()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            ver_tareas()
        elif opcion == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
