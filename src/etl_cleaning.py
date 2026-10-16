import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

NULL_TOKENS = {"", " ", "-", "–", "—", "null", "NULL", "None", "NaN"}

DROP_COLUMNS = {
    "Classificação de qualidade",
    "Classificação da taxa de engajamento",
    "Classificação da taxa de conversão",
    "Resultados (iniciais)",
    "Indicador de resultados (inicial)",
    "Orçamento do conjunto de anúncios",
    "Tipo de orçamento do conjunto de anúncios",
    "Término",
}

COLUMN_MAP = {
    "Início dos relatórios": "data_referencia",
    "Encerramento dos relatórios": "data_encerramento",
    "Identificação da campanha": "id_campanha",
    "Identificação do conjunto de anúncios": "id_conjunto",
    "Nome do conjunto de anúncios": "nome_conjunto",
    "Identificação do anúncio": "id_anuncio",
    "Nome do anúncio": "nome_anuncio",
    "Veiculação de anúncio": "status_veiculacao",
    "Configuração de atribuição": "janela_atribuicao",
    "Tipo de lance": "tipo_lance",
    "Lance": "lance_brl",
    "Última edição significativa": "ultima_edicao_iso",
    "Indicador de resultados": "indicador_resultado_raw",
    "Resultados": "resultados",
    "Custo por resultados": "custo_por_resultado_raw",
    "Índice de resultados": "indice_resultados_raw",
    "Valor gasto (BRL)": "valor_gasto_brl",
    "Impressões": "impressoes",
    "Alcance": "alcance",
    "Visualizações": "visualizacoes",
    "Cliques (todos)": "cliques_todos",
    "Cliques no link": "cliques_link",
    "Reproduções de vídeo": "video_plays",
    "Reproduções do vídeo por no mínimo 3 segundos": "video_3s",
    "ThruPlays de 15 segundos": "video_thruplay_15s",
    "Reproduções de 25% do vídeo": "video_p25",
    "Reproduções de 50% do vídeo": "video_p50",
    "Reproduções de 75% do vídeo": "video_p75",
    "Reproduções de 100% do vídeo": "video_p100",
}

INT_COLUMNS = {
    "resultados",
    "impressoes",
    "alcance",
    "visualizacoes",
    "cliques_todos",
    "cliques_link",
    "video_plays",
    "video_3s",
    "video_thruplay_15s",
    "video_p25",
    "video_p50",
    "video_p75",
    "video_p100",
}

FLOAT_COLUMNS = {
    "lance_brl",
    "custo_por_resultado_raw",
    "indice_resultados_raw",
    "valor_gasto_brl",
}

OBJECTIVE_LABELS = {
    "actions:link_click": "Trafego_Cliques_Link",
    "actions:onsite_conversion.messaging_conversation_started_7d": "Conversao_Mensagem_Iniciada",
}


def clean_token(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    stripped = val.strip()
    if stripped in NULL_TOKENS:
        return None
    return stripped


def parse_int(val: Optional[str]) -> int:
    cleaned = clean_token(val)
    if cleaned is None:
        return 0
    return int(float(cleaned))


def parse_float(val: Optional[str]) -> float:
    cleaned = clean_token(val)
    if cleaned is None:
        return 0.0
    return round(float(cleaned), 6)


def infer_objective_by_adset(nome_conjunto: str, indicador_raw: Optional[str]) -> str:
    if indicador_raw and indicador_raw in OBJECTIVE_LABELS:
        return OBJECTIVE_LABELS[indicador_raw]
    if "mensagem" in (nome_conjunto or "").lower():
        return "Conversao_Mensagem_Iniciada"
    return "Trafego_Cliques_Link"


def classify_row_activity(valor_gasto: float, impressoes: int, resultados: int) -> str:
    if valor_gasto > 0 or impressoes > 0:
        return "entrega_paga_ativa"
    if resultados > 0:
        return "conversao_tardia_atribuicao"
    return "inativo_sem_entrega"


def load_and_clean_csv(source_csv_path: Path) -> List[Dict[str, Any]]:
    cleaned_rows: List[Dict[str, Any]] = []
    with source_csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            if not any(raw_row.values()):
                continue
            record: Dict[str, Any] = {}
            for src_col, dst_col in COLUMN_MAP.items():
                if src_col in DROP_COLUMNS:
                    continue
                raw_val = raw_row.get(src_col)
                if dst_col in INT_COLUMNS:
                    record[dst_col] = parse_int(raw_val)
                elif dst_col in FLOAT_COLUMNS:
                    record[dst_col] = parse_float(raw_val)
                else:
                    record[dst_col] = clean_token(raw_val) or ""

            record["objetivo_padronizado"] = infer_objective_by_adset(
                record["nome_conjunto"], record["indicador_resultado_raw"]
            )
            record["tipo_registro_diario"] = classify_row_activity(
                record["valor_gasto_brl"], record["impressoes"], record["resultados"]
            )
            cleaned_rows.append(record)

    cleaned_rows.sort(key=lambda r: (r["data_referencia"], r["nome_conjunto"], r["nome_anuncio"]))
    return cleaned_rows
