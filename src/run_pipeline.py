import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from etl_cleaning import load_and_clean_csv
from metrics import aggregate_by_group, enrich_daily_kpis, run_data_quality_audit


def write_csv_file(target_path: Path, rows: List[Dict[str, Any]]) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with target_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_br_value(val: Any) -> str:
    if isinstance(val, float):
        return f"{val:.4f}".rstrip("0").rstrip(".").replace(".", ",")
    return str(val)


def write_powerbi_br_csv(
    target_path: Path, rows: List[Dict[str, Any]], col_mapping: Dict[str, str]
) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    headers = list(col_mapping.values())
    with target_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)
        for r in rows:
            row_out = [format_br_value(r.get(src_key, "")) for src_key in col_mapping.keys()]
            writer.writerow(row_out)


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    source_csv = base_dir / "data" / "raw" / "marketing-final-ad.csv"
    processed_dir = base_dir / "data" / "processed"

    all_cleaned = load_and_clean_csv(source_csv)
    all_enriched = enrich_daily_kpis(all_cleaned)
    active_daily = [
        r for r in all_enriched if r["tipo_registro_diario"] != "inativo_sem_entrega"
    ]

    ad_summary = aggregate_by_group(
        all_enriched,
        ["id_anuncio", "nome_anuncio", "id_conjunto", "nome_conjunto", "objetivo_padronizado"],
    )
    audit = run_data_quality_audit(all_enriched, ad_summary)

    write_csv_file(processed_dir / "fact_daily_active.csv", active_daily)
    write_csv_file(processed_dir / "agg_performance_by_ad.csv", ad_summary)

    br_ad_cols = {
        "nome_anuncio": "Nome do Anuncio",
        "nome_conjunto": "Conjunto de Anuncios",
        "objetivo_padronizado": "Objetivo",
        "primeira_data_ativa": "Data Inicio",
        "ultima_data_paga": "Data Fim",
        "dias_entrega_paga": "Dias Ativos",
        "valor_gasto_brl": "Valor Gasto (R$)",
        "impressoes": "Impressoes",
        "cliques_todos": "Cliques Totais",
        "cliques_link": "Cliques no Link",
        "resultados_totais": "Resultados",
        "cpr_ponderado_real_brl": "CPR (R$)",
        "cpm_brl": "CPM (R$)",
        "cpc_link_brl": "CPC no Link (R$)",
        "ctr_todos_pct": "CTR Total (%)",
        "ctr_link_pct": "CTR de Link (%)",
        "conv_clique_link_para_resultado_pct": "Conversao Clique para Resultado (%)",
        "video_plays": "Reproducoes de Video",
        "video_3s": "Reproducoes 3s",
        "video_thruplay_15s": "ThruPlays 15s",
        "hook_rate_imp_pct": "Hook Rate 3s (%)",
        "hold_rate_3s_to_thruplay_pct": "Hold Rate ThruPlay (%)",
        "custo_por_thruplay_brl": "Custo por ThruPlay (R$)",
        "retencao_p25_sobre_plays_pct": "Retencao Video 25 (%)",
        "retencao_p50_sobre_plays_pct": "Retencao Video 50 (%)",
        "retencao_p75_sobre_plays_pct": "Retencao Video 75 (%)",
        "retencao_p100_sobre_plays_pct": "Retencao Video 100 (%)",
    }
    write_powerbi_br_csv(processed_dir / "powerbi_pronto_por_anuncio.csv", ad_summary, br_ad_cols)

    audit_path = processed_dir / "data_quality_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
