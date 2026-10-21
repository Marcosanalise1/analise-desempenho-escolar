# 📚📊 Análise Integrada de Educação (Censo Escolar) e Nutrição (SISVAN)

> **Projeto Final de Formação em Análise de Dados** | **Autor:** Marcos Antonio Lima da Silva
> 
> Estudo analítico de grande escala integrando dados do **Censo Escolar (INEP)** e do **Sistema de Vigilância Alimentar e Nutricional (SISVAN - Ministério da Saúde)** via **Google BigQuery**, **Python** e **Power BI**, com foco em avaliar o impacto da infraestrutura escolar e da segurança alimentar no rendimento acadêmico no Brasil (2017–2023).

---

## 🛠️ Tecnologias e Ferramentas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=sqlite&logoColor=white)
![Google BigQuery](https://img.shields.io/badge/Google_BigQuery-669DF6?style=for-the-badge&logo=googlebigquery&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C94C?style=for-the-badge&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 🎯 Objetivos do Projeto

### 📌 Objetivo Geral
Relacionar as condições de infraestrutura das escolas públicas brasileiras (como acesso à água potável, saneamento e internet)[cite: 30] e os indicadores de saúde e nutrição dos alunos (SISVAN) com o respetivo rendimento escolar (**taxas de aprovação e abandono**) entre 2017 e 2023[cite: 30, 31].

### 🎯 Objetivos Específicos
* Extração e consolidação de bases massivas de dados públicos utilizando o **Google BigQuery** e **Python** (`pandas`/`google-cloud-bigquery`)[cite: 30].
* Tratamento de anomalias, prevenção de produtos cartesianos com uso de CTEs (Common Table Expressions)[cite: 31] e aplicação de fatores de escala[cite: 33].
* Gestão de lacunas temporais severas (subnotificação de 2020–2021 devido à pandemia de COVID-19).
* Construção de um dashboard executivo e interativo no **Power BI** para apoiar gestores públicos na identificação de gargalos geográficos[cite: 30, 34].

---

## 🛢️ Fontes de Dados & Pipeline ETL

Os dados brutos foram consultados diretamente no BigQuery através do projeto *Base dos Dados*[cite: 30]:
1. **Censo Escolar da Educação Básica (INEP):** Indicadores de infraestrutura, matrículas, aprovação e abandono da rede pública[cite: 30, 31].
2. **SISVAN (Ministério da Saúde):** Avaliações de peso/altura e indicadores de vulnerabilidade nutricional escolar[cite: 31, 34].
3. **Diretórios Brasileiros:** Mapeamento unificado de municípios e unidades federativas (UFs)[cite: 31, 32].

### ⚙️ Automação com Python (`desempenho_escolar.py`)
O script desenvolvido em Python realiza:
* Automação da conexão com o cliente BigQuery (`bigquery.Client`)[cite: 29].
* Extração parametrizada e salvamento em formato bruto (`RAW`)[cite: 29].
* Padronização automatizada de nomes de colunas (*snake_case*) e remoção de registos/colunas totalmente nulos[cite: 29].
* Exportação dos dados tratados para a camada limpa (`READY`)[cite: 29].

---

## 📐 Modelagem SQL e Regras de Negócio

A tabela analítica mestre foi consolidada no BigQuery através da seguinte lógica de agregação prévia por município e ano[cite: 31]:

```sql
CREATE OR REPLACE TABLE projeto-final-509412.ind_edu.master_saude_educacao_final AS
WITH censo_agregado AS (
    SELECT
        ano,
        id_municipio,
        SUM(quantidade_escolas) AS total_escolas_publicas,
        AVG(taxa_aprovacao) AS taxa_aprovacao_ef,
        AVG(taxa_abandono) AS taxa_abandono_ef,
        CAST(AVG(pet_agua_potavel) * 10000 AS INT64) AS pct_escolas_agua_potavel,
        CAST(AVG(pet_alimentacao) * 10000 AS INT64) AS pct_escolas_oferecem_alimentacao
    FROM `basedosdados.br_inep_censo_escolar.municipio`
    WHERE rede = 'Publica' AND ano BETWEEN 2017 AND 2023
    GROUP BY ano, id_municipio
),
sisvan_agregado AS (
    SELECT
        ano,
        id_municipio,
        SUM(total_avaliados) AS total_avaliados_escolares,
        SUM(qtd_vulnerabilidade_nutricional) AS qtd_vulnerabilidade_nutricional
    FROM `basedosdados.br_ms_sisvan.municipio`
    GROUP BY ano, id_municipio
)
SELECT
    c.ano,
    c.id_municipio,
    d.nome AS id_municipio_nome,
    d.sigla_uf,
    c.total_escolas_publicas,
    c.taxa_aprovacao_ef,
    c.taxa_abandono_ef,
    c.pct_escolas_agua_potavel,
    c.pct_escolas_oferecem_alimentacao,
    s.total_avaliados_escolares,
    s.qtd_vulnerabilidade_nutricional
FROM censo_agregado c
LEFT JOIN sisvan_agregado s ON c.id_municipio = s.id_municipio AND c.ano = s.ano
LEFT JOIN `basedosdados.br_bd_diretorios_brasil.municipio` d ON c.id_municipio = d.id_municipio;


## 💡 Principais Resultados & Insights Encontrados

* **Indicadores Nacionais Consolidados:**
  * Total de Matrículas Analisadas: **~43 Milhões**[cite: 26]
  * Taxa de Aprovação Média: **92,16%**[cite: 26]
  * Índice de Abandono Escolar: **5,18%**[cite: 26]
  * Cobertura Nutricional (SISVAN): **44,96%**[cite: 26]

* **Validação da Hipótese do Projeto:**
  * O cruzamento dos dados confirmou que municípios com maiores déficits em infraestrutura básica (falta de água potável, coleta de lixo, saneamento e internet) e maiores taxas de vulnerabilidade nutricional apresentam as maiores taxas de **abandono** e **reprovação escolar**[cite: 34].
  * Regiões que asseguram infraestrutura completa e cobertura alimentar constante mantêm taxas de aprovação significativamente mais altas e estáveis[cite: 34].

* **Municípios em Situação Crítica (Alta Vulnerabilidade Nutricional e Evasão):**
  * Destaques em alta taxa de abandono associada à vulnerabilidade alimentar: **Santa Rosa do Purus (AC)** (49,80% vul. nut. / 12,12% abandono) e **Jacareacanga (PA)** (46,56% vul. nut. / 12,77% abandono)[cite: 27].

---

## 🛠️ Tratamento de Anomalias no Power BI

* **Fator de Escala (10.000):** Indicadores percentuais foram multiplicados por 10.000 no SQL como inteiros para otimização de processamento e armazenamento no BigQuery, sendo revertidos no Power Query / DAX (`/ 10000`) para a escala percentual[cite: 33, 34].
* **Zeros vs. Nulos:** Aplicação da lógica DAX (`IF(ISBLANK([Medida]), BLANK(), [Medida])`) para diferenciar municípios sem dados daqueles com 0% real, evitando distorções nas médias estaduais[cite: 34].
* **Impacto da Pandemia (2020–2021):** Para contornar a queda drástica nos registros do SISVAN decorrente da interrupção das aulas presenciais na COVID-19, os dados foram mantidos como `BLANK` (sem invenção de médias) e acompanhados de *Tooltips* explicativos[cite: 34].
