import pandas as pd
import os
import urllib.parse
import unicodedata

# confiurando o github
usuario_github = "Darlan-Monteiro"
nome_repositorio = "Analise-dos-Brasileiros-Convocados-para-a-Copa"

# variaveis com o nome de cada pasta
pasta_jogadores = 'imagens jogadores'
pasta_ligas = 'logo das ligas'
pasta_clubes = 'logos dos clubes'
pasta_paises = 'logos dos paises'
# função para remover acentos e caracteres especiais dos nomes
def remover_acentos(texto):
    if not isinstance(texto, str): return ""
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if unicodedata.category(c) != 'Mn').strip()

# função para gerar o link do github, codificando os espaços e acentos, e respeitando a estrutura de pastas e arquivos
def gerar_url_padrao(nome_item, pasta_alvo):
    if pd.isna(nome_item) or str(nome_item).strip() == "": 
        return ""
    
    # pega o nome do arquivo e adiciona .png e cod espaços/acentos
    nome_arquivo = str(nome_item).strip() + ".png"
    
    pasta_alvo_web = urllib.parse.quote(pasta_alvo)
    nome_arquivo_web = urllib.parse.quote(nome_arquivo)
    
    # link padrão do endereço
    return f"https://raw.githubusercontent.com/{usuario_github}/{nome_repositorio}/refs/heads/main/{pasta_alvo_web}/{nome_arquivo_web}"

# bloco pa ajustar o bd dos jogadores
#leitura do bd
df_pre_lista = pd.read_excel('Pré Lista.xlsx')
df_convocados = pd.read_excel('jogadores_convo.xlsx')

# tratamento dos dados para unificar as bases e gerar os links das imagens
df_pre_lista['status_convocacao'] = 'Pré-Lista'
df_pre_lista['Clube'] = df_pre_lista['Jogadores pre lista'].str.extract(r'\((.*?)\)')
df_pre_lista['Nome'] = df_pre_lista['Jogadores pre lista'].str.split('(').str[0].str.strip()
df_pre_lista['Posicao'] = 'A Definir'

# função para limpar os nomes, removendo acentos, caracteres especiais e convertendo para maiúsculas
def limpar_nomes(serie_jogadores):
    return (serie_jogadores.str.split('(').str[0].str.replace(r'[^\w\s]', '', regex=True)
            .str.strip().str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))
# limpando os nomes dos convocados e pré-lista para comparação
lista_limpa_convocados = limpar_nomes(df_convocados['Jogadores']).tolist()
coluna_pre_lista_limpa = limpar_nomes(df_pre_lista['Jogadores pre lista'])
df_pre_lista.loc[coluna_pre_lista_limpa.isin(lista_limpa_convocados), 'status_convocacao'] = 'Convocado'

# lista para armazenar os links das imagens dos jogadores, verificando os arquivos locais e gerando os links do github
links_img_jogadores = []
arquivos_locais_jogadores = os.listdir(pasta_jogadores) if os.path.exists(pasta_jogadores) else []

# for para percorrer cada jogador da pré-lista, limpar os nomes e clubes, e tentar encontrar o arquivo correspondente na pasta local para gerar o link do github
for index, row in df_pre_lista.iterrows():
    nome = row['Nome']
    clube = str(row['Clube'])
    nome_limpo = remover_acentos(nome).upper()
    clube_limpo = remover_acentos(clube).upper()
    
    arquivo_alvo = None
    # bloco de condições para casos específicos onde o nome do jogador e clube podem gerar confusão, buscando o arquivo correto na pasta local
    if "DANILO" in nome_limpo and "BOTAFOGO" in clube_limpo:
        arquivo_alvo = next((arq for arq in arquivos_locais_jogadores if "Danilo" in arq and "Botafogo" in arq), None)
    elif "DANILO" in nome_limpo and "FLAMENGO" in clube_limpo:
        arquivo_alvo = next((arq for arq in arquivos_locais_jogadores if "Danilo" in arq and "Flamengo" in arq), None)
    elif "EDERSON" in nome_limpo and "ATALANTA" in clube_limpo:
        arquivo_alvo = next((arq for arq in arquivos_locais_jogadores if "Ederson" in arq and "Atalanta" in arq), None)
    else:
        nome_busca = remover_acentos(nome).replace(" ", "_")
        for arq in arquivos_locais_jogadores:
            if remover_acentos(arq).startswith(nome_busca):
                arquivo_alvo = arq
                break
                
    if arquivo_alvo:
        nome_arquivo_web = urllib.parse.quote(arquivo_alvo)
        links_img_jogadores.append(f"https://raw.githubusercontent.com/{usuario_github}/{nome_repositorio}/main/{pasta_jogadores}/{nome_arquivo_web}")
    else:
        links_img_jogadores.append("")
# adicionando a nova coluna de links das imagens ao dataframe e selecionando as colunas finais para exportar a base unificada dos jogadores
df_pre_lista['link_img'] = links_img_jogadores
df_jogadores_final = df_pre_lista[['Nome', 'Clube', 'status_convocacao', 'Link_Fbref', 'link_img', 'Posição']]
df_jogadores_final.to_csv('base_jogadores_unificada.csv', index=False, encoding='utf-8-sig')

# bloco para ajustar o bd dos clubes e ligas, gerando os links das imagens para cada dimensão
try:
    df_clubes = pd.read_excel('Dimensão Clubes.xlsx')
    
    # Gerando os links preservando a formatação real dos nomes na planilha
    df_clubes['Link_LogoClube'] = df_clubes['Clube'].apply(lambda x: gerar_url_padrao(x, pasta_clubes))
    df_clubes['Link_LogoLiga'] = df_clubes['Liga'].apply(lambda x: gerar_url_padrao(x, pasta_ligas))
    df_clubes['Link_Bandeira'] = df_clubes['País'].apply(lambda x: gerar_url_padrao(x, pasta_paises))
    
    df_clubes.to_csv('dimensao_clubes_final.csv', index=False, encoding='utf-8-sig')
    
except FileNotFoundError:
    print("Dimensão Clubes.xlsx não encontrada")

print("\nconcluído")
