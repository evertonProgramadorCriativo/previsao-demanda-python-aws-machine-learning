import io

import boto3
import pandas as pd
import streamlit as st

BUCKET = "demand-forecast-ogum"
REGIAO_AWS = "us-east-2"

st.set_page_config(page_title="Previsão de Demanda", layout="wide")


@st.cache_data(ttl=600)
def ler_csv(chave, colunas_data=None):
    s3 = boto3.client("s3", region_name=REGIAO_AWS)
    obj = s3.get_object(Bucket=BUCKET, Key=chave)
    return pd.read_csv(io.BytesIO(obj["Body"].read()), parse_dates=colunas_data or [])


def milhar(valor):
    return f"{valor:,.0f}".replace(",", ".")


historico = ler_csv("processed/vendas_historicas_limpo.csv", ["data"])
previsoes = ler_csv("predictions/previsoes_2025.csv", ["data"])
metricas = ler_csv("predictions/metricas_modelos.csv")
melhor_modelo = metricas[metricas["modelo"] != "Baseline (lag_7)"].iloc[0]["modelo"]

# ---------- filtros ----------
st.sidebar.header("Filtros")
produtos = sorted(historico["produto"].unique())
regioes = sorted(historico["regiao"].unique())
sel_produtos = st.sidebar.multiselect("Produto", produtos, default=produtos)
sel_regioes = st.sidebar.multiselect("Região", regioes, default=regioes)

hist = historico[historico["produto"].isin(sel_produtos) & historico["regiao"].isin(sel_regioes)]
prev = previsoes[previsoes["produto"].isin(sel_produtos) & previsoes["regiao"].isin(sel_regioes)]

st.title("Previsão de Demanda e Vendas")
st.caption(f"Dados de vendas simulados, lidos do S3 · Modelo usado nas previsões: {melhor_modelo}")

if hist.empty or prev.empty:
    st.warning("Escolha pelo menos um produto e uma região.")
    st.stop()

# ---------- números principais ----------
erro_pct = prev["erro_abs"].sum() / prev["real"].sum() * 100
c1, c2, c3, c4 = st.columns(4)
c1.metric("Receita total (2022 a 2025)", milhar(hist["receita"].sum()))
c2.metric("Unidades vendidas em 2025", milhar(prev["real"].sum()))
c3.metric("Erro médio por dia", f"{prev['erro_abs'].mean():.1f} unidades")
c4.metric("Erro em % das vendas", f"{erro_pct:.1f}%")

aba1, aba2, aba3 = st.tabs(["Real x Previsto", "Sazonalidade", "Erro do modelo"])

# ---------- aba 1 ----------
with aba1:
    st.subheader("2025: vendas reais x previstas")
    mostrar_base = st.checkbox("Mostrar também o chute simples (repetir a semana passada)")
    colunas = ["real", "previsto"] + (["previsto_baseline"] if mostrar_base else [])
    st.line_chart(prev.groupby("data")[colunas].sum())

# ---------- aba 2 ----------
with aba2:
    hist = hist.assign(ano=hist["data"].dt.year, mes=hist["data"].dt.month)
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Unidades por mês, ano a ano")
        mensal = hist.groupby(["mes", "ano"])["quantidade_vendida"].sum().unstack("ano")
        mensal.columns = mensal.columns.astype(str)
        st.line_chart(mensal)

    with col_b:
        st.subheader("Média de unidades por dia da semana")
        diario_hist = hist.groupby("data")["quantidade_vendida"].sum()
        media_semana = diario_hist.groupby(diario_hist.index.dayofweek).mean()
        media_semana.index = ["1-Seg", "2-Ter", "3-Qua", "4-Qui", "5-Sex", "6-Sáb", "7-Dom"]
        st.bar_chart(media_semana)

# ---------- aba 3 ----------
with aba3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Erro médio por mês (unidades)")
        erro_mes = prev.assign(mes=prev["data"].dt.month).groupby("mes")["erro_abs"].mean()
        st.bar_chart(erro_mes)

    with col_b:
        st.subheader("Erro médio por produto (unidades)")
        st.bar_chart(prev.groupby("produto")["erro_abs"].mean())

    st.subheader("Comparação dos modelos (todos os dados de 2025)")
    st.dataframe(metricas, hide_index=True)