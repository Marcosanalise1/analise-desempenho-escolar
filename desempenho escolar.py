import os
import re
import sys
from google.cloud import bigquery
import pandas as pd

# ============================
# Configurações
# ============================
PROJECT_ID = "projeto-final-509412"

# Alterado para 'US' (ou None), pois tabelas públicas/base dos dados residem em 'US'
DATASET_LOCATION = "US"

# Garantir que os diretórios locais existam antes de salvar
RAW_DIR = "C:/Users/marco/Documents/modulo 4/Data/Raw"
READY_DIR = "C:/Users/marco/Documents/modulo 4/Data/Ready"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(READY_DIR, exist_ok=True)

# ======================
# Ambiente / Debug
# ======================
print("=== Ambiente de Execução ===")
print("Python executable:", sys.executable)
print("Python version:", sys.version.splitlines()[0])
print(
    "GOOGLE_APPLICATION_CREDENTIALS:",
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
)
print()

# ======================
# Cliente BigQuery
# ======================
client = bigquery.Client(project=PROJECT_ID)


def run_query(query: str) -> bigquery.job.QueryJob:
    """Executa uma query no BigQuery respeitando a região do dataset."""
    return client.query(query, location=DATASET_LOCATION)


# ==============================================================
# Dicionário de Consultas SQL (Adicione suas queries aqui)
# ==============================================================
queries = {
    "master_saude_educacao": """
        SELECT * 
        FROM `projeto-final-509412.ind_edu.master_saude_educacao`
    """
    # Adicione mais tabelas se necessário:
    # "outra_tabela": "SELECT * FROM ... "
}

# ==============================================================
# 5. EXTRAÇÃO DOS DATASETS BRUTOS (RAW)
# ==============================================================
print(">>> Extraindo dados do BigQuery (RAW)")

dfs = {}

for name, query in queries.items():
    print(f">>> Extraindo dados brutos: {name}")
    df = run_query(query).to_dataframe()
    print(f"Total de registros extraídos para {name}: {len(df)}")

    # Salva em CSV bruto
    raw_path = os.path.join(RAW_DIR, f"{name}_bruto.csv")
    df.to_csv(raw_path, index=False)

    # Mantém em memória
    dfs[name] = df

# ==============================================================
# 6. PADRONIZAÇÃO DOS NOMES DAS COLUNAS
# ==============================================================
def normalize_column(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r"[^\w]+", "_", col)
    col = re.sub(r"_+", "_", col)
    return col.strip("_")


for name, df in dfs.items():
    df.columns = [normalize_column(c) for c in df.columns]
    print(f"Colunas padronizadas para {name}: {list(df.columns)}")

# ==============================================================
# 7. REMOÇÃO DE COLUNAS SEM VALORES (COM LOG)
# ==============================================================
print("\n>>> Removendo colunas totalmente vazias")

for name, df in dfs.items():
    cols_before = set(df.columns)
    df = df.dropna(axis=1, how="all")
    cols_after = set(df.columns)

    removed_columns = sorted(list(cols_before - cols_after))
    print(f"[{name}] Total de colunas removidas: {len(removed_columns)}")

    if removed_columns:
        print("Colunas excluídas:")
        for col in removed_columns:
            print(f"- {col}")
    else:
        print("Nenhuma coluna foi removida.")

    dfs[name] = df

# ==============================================================
# 8. REMOÇÃO DE LINHAS TOTALMENTE VAZIAS
# ==============================================================
print("\n>>> Removendo registros totalmente vazios")

for name, df in dfs.items():
    rows_before = len(df)
    df = df.dropna(how="all")
    rows_after = len(df)

    removed_rows = rows_before - rows_after
    print(f"[{name}] Total de linhas removidas: {removed_rows}")

    dfs[name] = df

# ==============================================================
# 9. SALVAMENTO DO DATASET LIMPO (READY)
# ==============================================================
print("\n>>> Salvando datasets limpos")

for name, df in dfs.items():
    ready_path = os.path.join(READY_DIR, f"{name}_final.csv")
    df.to_csv(ready_path, index=False)

    print(f"Arquivo salvo com sucesso: {ready_path}")
    print(f"[{name}] Linhas finais: {len(df)}")
    print(f"[{name}] Colunas finais: {df.shape[1]}")
    print()