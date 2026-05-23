import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

# bloco para acessar o arquivo gerado no main.py, filtrar os jogadores com links válidos, e iniciar o processo de scraping das estatísticas no site fbref.com
try:
    df_alvos = pd.read_csv('base_jogadores_unificada.csv')
except FileNotFoundError:
    print("arquivo base_jogadores_unificada.csv não encontrado. o arquivo main.py tem q ser executado antes")
    exit()

# filtra valores vazios na coluna de link
df_alvos = df_alvos.dropna(subset=['Link_Fbref'])
df_alvos = df_alvos[df_alvos['Link_Fbref'].str.strip() != ""]

total_jogadores = len(df_alvos)
print(f"{total_jogadores} jogadores com links válidos\n")

# configurando o undetected_chromedriver para acessar as páginas dos jogadores e extrair as estatísticas, com tratamento de erros e mensagens de progresso
options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=148)

# lista para armazenar os dataframes de estatísticas de cada jogador, que serão consolidados no final
todas_as_estatisticas = []

# bloco principal de scraping, com tratamento para casos onde a tabela padrão de estatísticas não é encontrada, e mensagens de progresso para cada jogador
try:
    for index, linha in df_alvos.iterrows():
        nome = linha['Nome']
        link = linha['Link_Fbref']
        
        print(f"{index+1} de {total_jogadores} - {nome}")
        driver.get(link)
        time.sleep(6) 
        
        html_puro = driver.page_source
        html_limpo = re.sub(r'', '', html_puro)
        # tratamento para casos onde o conteúdo pode estar em branco ou não ser uma string válida
        try:
            soup = BeautifulSoup(html_limpo, 'html.parser')
            tabelas_html = soup.find_all('table', id=re.compile(r'^stats_standard'))
            tabela_encontrada = False
            # bloco para processar as tabelas encontradas, buscando a tabela de estatísticas padrão, e tratando casos onde os headers podem ter colunas repetidas, garantindo nomes únicos para cada coluna
            for tabela in tabelas_html:
                thead = tabela.find('thead')
                tbody = tabela.find('tbody')
                if not thead or not tbody: continue
                
                linhas_header = thead.find_all('tr')
                if not linhas_header: continue
                
                ultima_linha_header = linhas_header[-1]
                colunas_brutas = [th.text.strip() for th in ultima_linha_header.find_all('th')]
                # tratamento para colunas repetidas, adicionando um sufixo numérico para garantir nomes únicos
                colunas_unicas = []
                for col in colunas_brutas:
                    col_nome = col
                    contador = 1
                    while col_nome in colunas_unicas:
                        col_nome = f"{col}_{contador}"
                        contador += 1
                    colunas_unicas.append(col_nome)
                # bloco para processar as linhas de dados da tabela, garantindo que o número de colunas corresponda ao header, e armazenando os dados em um dataframe para cada jogador
                dados_brutos = []
                for linha_tb in tbody.find_all('tr'):
                    if linha_tb.get('class') and 'thead' in linha_tb.get('class'):
                        continue
                    # tratamento para garantir que cada linha de dados tenha o mesmo número de colunas do header, evitando erros na criação do dataframe    
                    linha_dados = []
                    for celula in linha_tb.find_all(['th', 'td']):
                        linha_dados.append(celula.text.strip())
                    
                    if len(linha_dados) == len(colunas_unicas):
                        dados_brutos.append(linha_dados)
                # tratamento para casos onde a tabela pode estar vazia ou não conter dados válidos, evitando erros na criação do dataframe
                if dados_brutos:
                    df_stats = pd.DataFrame(dados_brutos, columns=colunas_unicas)
                    df_stats.insert(0, 'Nome', nome)
                    todas_as_estatisticas.append(df_stats)
                    tabela_encontrada = True
                    break 
                
            if not tabela_encontrada:
                print(f"tabela Standard Stats não encontrada pra {nome}")
                
        except Exception as e:
            print(f"erro na tabelas do {nome}: {e}")

finally:
    driver.quit()

if todas_as_estatisticas:
    df_final = pd.concat(todas_as_estatisticas, ignore_index=True)
    nome_arquivo = 'estatisticas_fbref_completas.csv'
    df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
    print(f"{nome_arquivo}' gerado com {len(df_final)} linhas de dados.")
else:
    print("nenhum dado foi gerado.")