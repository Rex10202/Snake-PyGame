import bcrypt

password = "admin123"  # Cambia esto por la contraseña deseada
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed_password.decode('utf-8'))