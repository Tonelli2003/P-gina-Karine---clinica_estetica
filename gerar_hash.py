from werkzeug.security import generate_password_hash

# A senha temporária que queremos usar
senha_para_criptografar = 'mudar123'

# O programa vai gerar o hash usando a SUA versão da biblioteca
hash_gerado = generate_password_hash(senha_para_criptografar)

print("\n================== SEU HASH PESSOAL ==================")
print("\nCopie a linha de código abaixo completa (tudo que está entre as aspas simples):\n")
print(f"'{hash_gerado}'")
print("\n====================================================\n")