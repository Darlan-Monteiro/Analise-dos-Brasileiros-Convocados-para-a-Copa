# ⚽ Engenharia de Dados & Scraping: Seleção Brasileira

Este repositório contém a primeira fase do projeto de análise de desempenho dos 55 jogadores da pré-lista da Seleção Brasileira para a Copa. O foco desta etapa é a **Engenharia de Dados, Limpeza e Web Scraping**, criando a base fundamental para um futuro dashboard de Scout de Elite.

## Objetivo do Projeto
O futebol moderno exige dados precisos. O objetivo destes scripts é automatizar a extração de estatísticas detalhadas de jogo diretamente do FBref e consolidar URLs de imagens (jogadores, clubes e ligas) hospedadas neste próprio repositório, garantindo um banco de dados limpo, relacional e pronto para o Power BI.

## Arquitetura e Scripts

O processo de ETL (Extract, Transform, Load) foi dividido em dois scripts Python:

### 1. `main.py` (Tratamento e Modelagem)
* Cruza os dados da lista de convocados oficiais com a pré-lista de 55 nomes usando `pandas`.
* Padroniza nomes e remove caracteres especiais via `unicodedata` e expressões regulares (Regex).
* Gera links absolutos dinâmicos para as imagens armazenadas no GitHub, resolvendo colisões de nomes (ex: diferenciando "Danilo" do Flamengo e "Danilo" do Botafogo).
* **Saída:** `base_jogadores_unificada.csv` e `dimensao_clubes_final.csv`.

### 2. `scraping_jogadores.py` (Extração de Dados em Massa)
* Utiliza `undetected_chromedriver` e `BeautifulSoup` para contornar bloqueios de bots e acessar as páginas dos jogadores no FBref.
* Varre dinamicamente as tabelas de "Standard Stats", garantindo que colunas repetidas nos cabeçalhos HTML sejam renomeadas corretamente para evitar falhas no Dataframe.
* **Saída:** `estatisticas_fbref_completas.csv` (contendo todo o histórico de minutos, gols, assistências, etc., pronto para a criação de métricas P90).

## Tecnologias Utilizadas
* **Python 3.x**
* **Pandas:** Manipulação e limpeza de dados estruturados.
* **BeautifulSoup4:** Parsing do HTML para extração cirúrgica das tabelas.
* **Undetected-Chromedriver / Selenium:** Automação de navegação web.

## Próximos Passos
Os arquivos `.csv` gerados por esta pipeline serão consumidos pelo Power BI para a criação de um Dashboard tático, focando em métricas de eficiência (P90), consistência física e radar de atributos.
