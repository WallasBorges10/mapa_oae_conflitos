# modules/search.py
import pandas as pd

def search_oae(searchterm: str, df: pd.DataFrame) -> list[tuple[str, str]]:
    """Search function for OAE data."""
    # Converte para string e remove valores nulos
    df = df.dropna(subset=['cod_sgo', 'descr_obra'])
    df['cod_sgo'] = df['cod_sgo'].astype(str)
    df['descr_obra'] = df['descr_obra'].astype(str)
    
    if not searchterm:
        return []
    
    searchterm = searchterm.lower()
    
    # Cria colunas combinadas para pesquisa nos dois formatos
    df['cod_desc'] = df['cod_sgo'] + " - " + df['descr_obra']
    df['desc_cod'] = df['descr_obra'] + " - " + df['cod_sgo']
    
    # Busca em todas as colunas relevantes
    mask = (df['cod_sgo'].str.lower().str.contains(searchterm)) | \
           (df['descr_obra'].str.lower().str.contains(searchterm)) | \
           (df['cod_desc'].str.lower().str.contains(searchterm)) | \
           (df['desc_cod'].str.lower().str.contains(searchterm))
    
    results = df.loc[mask]
    
    # Formata os resultados para exibição (usando o formato código - descrição)
    suggestions = [
        (f"{row['cod_sgo']} - {row['descr_obra']}", row['cod_sgo'])
        for _, row in results.iterrows()
    ]
    
    # Remove duplicados mantendo a primeira ocorrência
    seen = set()
    unique_suggestions = []
    for sug in suggestions:
        if sug[0] not in seen:
            seen.add(sug[0])
            unique_suggestions.append(sug)
    
    return unique_suggestions