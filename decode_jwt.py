#!/usr/bin/env python3
import base64
import json
import sys
import struct
import time

# External dependencies
import requests
import jwt  # Requires: pip install PyJWT[crypto]
from jwt.api_jwk import PyJWK

def get_github_public_keys(issuer=None):
    """
    Obtiene las claves públicas de GitHub para verificar los tokens JWT.
    
    Args:
        issuer (str, optional): El emisor del token para determinar qué claves obtener
    
    Returns:
        dict: Un diccionario con los "kid" como claves y las claves públicas como valores
    """
    # Para tokens de GitHub Actions, necesitamos obtener las claves del emisor correcto
    if issuer and 'actions.githubusercontent.com' in issuer:
        # GitHub Actions usa un endpoint JWKS estándar
        url = "https://token.actions.githubusercontent.com/.well-known/jwks"
        
        try:
            response = requests.get(url, timeout=5)  # Añadir timeout para evitar esperas indefinidas
            response.raise_for_status()  # Lanzar excepción si no es 2xx
            
            jwks = response.json()
            keys = {}
            
            # Procesar las claves del JWKS de forma eficiente
            if 'keys' in jwks:
                for key in jwks['keys']:
                    if 'kid' in key:
                        try:
                            # Convertir directamente la clave JWK a objeto criptográfico
                            keys[key['kid']] = PyJWK.from_dict(key).key
                        except Exception:
                            pass  # Si falla, simplemente continuar con la siguiente clave
                
                return keys
        except requests.RequestException:
            pass  # Fallar silenciosamente y probar con el siguiente endpoint
    
    # Fallback a las claves de GitHub API (solo si es necesario)
    try:
        response = requests.get("https://api.github.com/meta", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if 'hooks' in data and 'public_key' in data['hooks']:
            return {'default': data['hooks']['public_key']}
    except requests.RequestException:
        pass
    
    return {}

def decode_jwt(token, verify_signature=False):
    """
    Decodifica un token JWT y opcionalmente verifica la firma.
    
    Args:
        token (str): El token JWT a decodificar
        verify_signature (bool): Si es True, verifica la firma del token
        
    Returns:
        str: El owner_id o None si no se pudo decodificar o no existe ese campo
    """
    try:
        if verify_signature:
            # Extraer el encabezado para obtener el kid (Key ID)
            header_part = token.split('.')[0]
            padding = '=' * (4 - len(header_part) % 4)
            base64_str = (header_part + padding).replace('-', '+').replace('_', '/')
            header = json.loads(base64.b64decode(base64_str))
            
            # Obtener el "kid" (Key ID) que identifica la clave pública a usar
            kid = header.get('kid', 'default')
            
            # Obtener las claves públicas de GitHub
            public_keys = get_github_public_keys()
            if kid not in public_keys:
                return None
            
            # Verificar la firma con la menor cantidad de validaciones posible
            decoded = jwt.decode(
                token,
                public_keys[kid],
                algorithms=['RS256'],
                options={
                    "verify_signature": True,
                    "verify_aud": False,
                    "verify_exp": False
                }
            )
        else:
            # Decodificar directamente sin verificación
            decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Retornar el owner_id si existe
        return decoded.get('owner_id')
        
    except Exception:
        return None

def decode_github_node_id(node_id):
    """
    Decodifica un ID de GitHub en formato nodeid (ej: 'O_kgDOB9m9vA')
    y devuelve el ID numérico para la API REST.
    
    Args:
        node_id (str): El ID de GitHub a decodificar
        
    Returns:
        int: El ID numérico decodificado o None si no se pudo decodificar
    """
    # Separar el prefijo (tipo de entidad) del resto
    parts = node_id.split('_', 1)
    if len(parts) != 2:
        print(f"Formato de ID inválido: {node_id}")
        return None
    
    try:
        # Método que funciona para convertir node_id a ID numérico
        encoded_id = parts[1]  # Por ejemplo: 'kgDOB9m9vA'
        
        # Reemplazar caracteres especiales de base64url
        base64_str = encoded_id.replace('-', '+').replace('_', '/')
        
        # Añadir padding si es necesario
        padding = '=' * (4 - len(base64_str) % 4) if len(base64_str) % 4 != 0 else ''
        base64_str += padding
        
        # Decodificar
        decoded = base64.b64decode(base64_str)
        
        # Extraer los últimos 4 bytes como un entero de 32 bits
        if len(decoded) >= 4:
            numeric_id = struct.unpack('>I', decoded[-4:])[0]
            return numeric_id
        
        return None
    except Exception as e:
        print(f"Error al decodificar GitHub node_id: {e}")
        return None

def fetch_github_org_info(org_id):
    """
    Obtiene información de una organización de GitHub usando la API REST.
    
    Args:
        org_id (int): El ID numérico de la organización
        
    Returns:
        dict: Los datos de la organización o None si hubo un error
    """
    url = f"https://api.github.com/organizations/{org_id}"
    
    try:
        response = requests.get(
            url, 
            headers={
                "Accept": "application/vnd.github.v3+json",
                # No incluimos un token de autenticación aquí porque estamos
                # accediendo a información pública
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener datos de GitHub: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error al realizar la petición a GitHub: {e}")
        return None

def get_org_name_from_jwt(token):
    """
    Obtiene el nombre de la organización a partir de un token JWT.
    
    Args:
        token (str): El token JWT a decodificar
        
    Returns:
        str: El nombre de la organización o None si no se pudo obtener
    """
    try:
        # Obtener el owner_id del token de manera eficiente
        owner_id = decode_jwt(token)
        if not owner_id or not owner_id.startswith('O_'):
            return None
        
        # Decodificar el node_id de GitHub
        numeric_id = decode_github_node_id(owner_id)
        if not numeric_id:
            return None
            
        # Obtener información de la organización y extraer el login
        org_info = fetch_github_org_info(numeric_id)
        return org_info.get('login') if org_info else None
            
    except Exception:
        return None

def verify_github_jwt(token):
    """
    Verifica si un JWT está firmado por GitHub de manera eficiente.
    
    Args:
        token (str): El token JWT a verificar
        
    Returns:
        bool: True si el token está firmado válidamente por GitHub, False en caso contrario
    """
    try:
        # Decodificar sin verificar firma para obtener información básica
        decoded_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Obtener el encabezado del token
        header_part = token.split('.')[0]
        padding = '=' * (4 - len(header_part) % 4)
        base64_str = (header_part + padding).replace('-', '+').replace('_', '/')
        header = json.loads(base64.b64decode(base64_str))
        
        # Verificación rápida del algoritmo
        if header.get('alg') != 'RS256':
            return False
        
        # Verificar si el emisor es de GitHub
        iss = decoded_payload.get('iss')
        github_issuers = ('api.github.com', 'github.com', 'actions.githubusercontent.com')
        
        if not iss or not any(github_issuer in str(iss) for github_issuer in github_issuers):
            return False
        
        # Obtener el identificador de clave (kid)
        kid = header.get('kid')
        if not kid:
            return False
        
        # Obtener las claves públicas
        public_keys = get_github_public_keys(iss)
        if not public_keys or kid not in public_keys:
            return False
        
        # Obtener la clave pública correspondiente
        public_key = public_keys[kid]
        
        # Opciones de verificación optimizadas (se prueban en orden de probabilidad de éxito)
        verification_options = [
            # Opción 1: Sin verificar audiencia ni tiempo de expiración (máxima flexibilidad)
            {"verify_signature": True, "verify_aud": False, "verify_exp": False},
            # Opción 2: Sin verificar audiencia
            {"verify_signature": True, "verify_aud": False},
            # Opción 3: Sin verificar tiempo de expiración
            {"verify_signature": True, "verify_exp": False},
            # Opción 4: Verificación completa
            {"verify_signature": True}
        ]
        
        # Intentar verificar la firma con las diferentes opciones
        for options in verification_options:
            try:
                jwt.decode(token, public_key, algorithms=['RS256'], options=options)
                return True  # Si llegamos aquí, la firma es válida
            except jwt.InvalidTokenError:
                continue  # Intentar con la siguiente opción
        
        return False  # Ninguna opción funcionó
    
    except Exception:
        return False  # Cualquier error inesperado

def get_org_name_and_verify_from_token(token):
    print(token)
    # Verificar si el token está firmado por GitHub
    is_valid = verify_github_jwt(token)
    print(f"¿El token está firmado por GitHub?: {'Sí' if is_valid else 'No'}")
    
    # Obtener el nombre de la organización si es válido
    if is_valid:
        org_name = get_org_name_from_jwt(token)
        if org_name:
            print(f"Organización: {org_name}")
            return org_name
        else:
            print("No se pudo obtener el nombre de la organización.")
            return None
    else:
        print("El token no es válido.")
        return None

if __name__ == "__main__":
    # Verificación rápida de argumentos
    if len(sys.argv) != 2:
        print("Uso: python3 decode_jwt.py <token_jwt>")
        sys.exit(1)
    
    # Usar el token proporcionado como argumento
    token = sys.argv[1]
    get_org_name_and_verify_from_token(token)



