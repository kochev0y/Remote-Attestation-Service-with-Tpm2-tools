from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

# Создание основного ключа
def create_primary_key():
    subprocess.run(["tpm2_createprimary", "-C", "e", "-c", "primary.ctx"], check=True)

# Создание ключа шифрования
def create_key():
    subprocess.run(["tpm2_create", "-C", "primary.ctx", "-u", "key.pub", "-r", "key.priv"], check=True)

# Загрузка ключа в TPM-чип
def load_key():
    subprocess.run(["tpm2_load", "-C", "primary.ctx", "-u", "key.pub", "-r", "key.priv", "-c", "key.ctx"], check=True)

# Запрос на TPM-чип для получения данных
def quote():
    subprocess.run(["tpm2_quote", "-Q", "-c", "key.ctx", "-l", "sha256:8,9", "-s", "quote.bin"], check=True)

    with open('quote.bin', "rb") as f:
        quote = f.read().hex()
        return quote

# Запрос на TPM-чип для получения публичного ключа и значений PCR
def read_public():
    subprocess.run(["tpm2_readpublic", "-c", "primary.ctx", "-o", "pubkey.dat"], check=True)

    subprocess.run(["tpm2_pcrread", "sha256:8,9", "-o", "pcr89.bin"], check=True)

    with open('pubkey.dat', "rb") as f:
        pubkey = f.read().hex()

    with open('pcr89.bin', "rb") as f:
        pcr_89 = f.read().hex()

    # Разделение значений PCR на отдельные переменные
    pcr_8 = pcr_89[:64]
    pcr_9 = pcr_89[64:]

    return pubkey, pcr_8, pcr_9

@app.route('/challenge')
def challenge():
    create_primary_key()
    create_key()
    load_key()
    quote_hex = quote()

    # Возвращает результат в виде JSON
    return jsonify({"quote": quote_hex})

@app.route('/certificate')
def certificate():
    pubkey_hex, pcr_8_hex, pcr_9_hex = read_public()

    # Возвращает результат в виде JSON
    return jsonify({"pubkey": pubkey_hex, "PCR_8": pcr_8_hex, "PCR_9": pcr_9_hex})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
