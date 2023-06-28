from flask import Flask, render_template, request
import subprocess
import json
import os
import sys
import mysql.connector

app = Flask(__name__)

# Função para ler as informações dos domínios do banco de dados


def read_domain_info_from_database():
    # Conecta ao banco de dados
    db_connection = mysql.connector.connect(
        host='172.16.179.36',
        user='WP',
        password='123WP',
        database='pt_WordPress1'
    )
    db_cursor = db_connection.cursor()
    query = "SELECT * FROM domain_info2"
    db_cursor.execute(query)
    results = []
    # Lê cada linha do resultado e cria um dicionário com as informações
    for row in db_cursor.fetchall():
        result = {
            'domain': row[1],
            'ip': row[2],
            'version': row[3],
            'host': row[4],
            'name_servers': row[5]
        }
        results.append(result)
    # Fecha a conexão com o banco de dados
    db_connection.close()
    return results


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        wp_spider_path = '../ptfingerprintwp/spiders/WPfingerWP.py'
        version_spider_path = '../ptfingerprintwp/spiders/version.py'

        # Comando para executar o spider que busca websites portugueses com WordPress
        wp_command = ['scrapy', 'runspider', wp_spider_path]
        process = subprocess.Popen(wp_command)
        process.wait()  # Espera a conclusão do processo

       #Comando para executar o spider que verifica se os domínios são realmente WordPress e obtém informações adicionais
        version_command = ['scrapy', 'runspider', version_spider_path]
        process = subprocess.Popen(version_command)
        process.wait()  # Espera a conclusão do processo

        # Lê as informações dos domínios do banco de dados
        results = read_domain_info_from_database()

        return render_template('index.html', results=results)

    return render_template('index.html', results='home')


@app.route('/sobrenos')
def sobrenos():
    return render_template('sobreNos.html')


@app.route('/contato')
def contato():
    return render_template('contactar.html')


@app.route('/scan_wp', methods=['GET', 'POST'])
def scan_wp():
    if request.method == 'POST':
        domain = request.form.get('domain')
        spider_path = 'D:/2-Ano/2 - semestre/PW/CRYPTO/Mine-Project/ptfingerprintwp/spiders/scan_wp.py'
        output_path = './scan_output.json'

        # Remove o arquivo de saída existente, se existir
        if os.path.exists(output_path):
            os.remove(output_path)

        # Comando para executar o spider que faz a varredura em um site WordPress específico
        #command = ['scrapy', 'runspider', spider_path,
         #          '-a', f'domain={domain}', '-o', 'scan_output.json']
        #process = subprocess.Popen(command)
        #process.wait()  # Espera a conclusão do processo

        results = 'home'
        if os.path.exists(output_path):
            with open(output_path, 'r') as file:
                results = json.load(file)
                print(results[0])
                return render_template('scan_wp.html', results=results[0])

    return render_template('scan_wp.html', results='home')


if __name__ == '__main__':
    app.run()
