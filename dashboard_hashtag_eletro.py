import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Eletro", layout="wide")
st.title("📊 Dashboard de Vendas — Eletro")



# Funções utilitárias

@st.cache_data
def ler_excel(arquivo):
    df = pd.read_excel(arquivo)
    return df

def tratar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    # Data da Venda: tratar serial do Excel (número) e strings
    if "Data da Venda" in df.columns:
        if pd.api.types.is_numeric_dtype(df["Data da Venda"]):
            df["Data da Venda"] = pd.to_datetime(df["Data da Venda"], unit="d", origin="1899-12-30", errors="coerce")
        else:
            df["Data da Venda"] = pd.to_datetime(df["Data da Venda"], errors="coerce")

    # Números
    for col in ["Faturamento", "Preço Unitário"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Qtd Vendida" in df.columns:
        df["Qtd Vendida"] = pd.to_numeric(df["Qtd Vendida"], errors="coerce").astype("Int64")

    return df

def carregar_base_exemplo() -> pd.DataFrame:
    dados = {
        "SKU Vendido": ["A101", "A102", "A103", "B201", "B202", "B203", "C301", "C302", "C303", "C304",
                        "D401", "D402", "E501", "E502", "F601", "F602", "G701", "H801", "I901", "J001"],
        "Qtd Vendida": [10, 5, 8, 7, 4, 6, 12, 3, 9, 15, 2, 18, 6, 7, 5, 4, 8, 11, 13, 9],
        "Produto": ["Smartphone X", "Smartphone Y", "Smartphone Z", "TV 50\"", "TV 65\"", "TV 75\"",
                    "Notebook A", "Notebook B", "Notebook C", "Notebook D",
                    "Geladeira A", "Geladeira B", "Micro-ondas A", "Micro-ondas B",
                    "Tablet A", "Tablet B", "Caixa de Som", "Fone Bluetooth", "Câmera Ação", "Console Z"],
        "Marca": ["TechOne", "TechOne", "MegaCell", "VisioMax", "VisioMax", "VisioMax",
                  "NotePro", "NotePro", "NotePro", "NotePro",
                  "FrioMax", "FrioMax", "HeatWave", "HeatWave",
                  "TabGo", "TabGo", "SoundUp", "HearMe", "CamGo", "PlayMax"],
        "Categoria": ["Celular", "Celular", "Celular", "Televisão", "Televisão", "Televisão",
                      "Notebook", "Notebook", "Notebook", "Notebook",
                      "Eletrodoméstico", "Eletrodoméstico", "Eletrodoméstico", "Eletrodoméstico",
                      "Tablet", "Tablet", "Áudio", "Acessório", "Câmeras", "Games"],
        "Preço Unitário": [1500, 1800, 2000, 2500, 3500, 4500, 3000, 3200, 2800, 3500, 4200, 3800, 800, 900, 1200, 1400, 600, 250, 1100, 2800],
        "Faturamento": [15000, 9000, 16000, 17500, 14000, 27000, 36000, 9600, 25200, 52500, 8400, 68400, 4800, 6300, 6000, 5600, 4800, 2750, 14300, 25200],
        "Loja": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "São Paulo", "Rio de Janeiro", "Belo Horizonte",
                 "São Paulo", "Rio de Janeiro", "Belo Horizonte", "São Paulo",
                 "Curitiba", "Curitiba", "Porto Alegre", "Porto Alegre", "Salvador", "Salvador", "Fortaleza", "Fortaleza", "Recife", "Recife"],
        "Data da Venda": pd.date_range("2024-01-01", periods=20, freq="15D"),
        "Tipo Loja": ["Física", "Online"] * 10,
        "Código Cliente": [101 + i for i in range(20)]
    }
    return pd.DataFrame(dados)


# Entrada de dados

arquivo = st.file_uploader("📂 Envie o arquivo Base Vendas.xlsx", type=["xlsx"])

if arquivo:
    df = ler_excel(arquivo)
    df = tratar_tipos(df)
else:
    st.warning("⚠ Nenhum arquivo enviado. Modo demonstração ativado com base de exemplo.")
    df = carregar_base_exemplo()


# Filtros

with st.sidebar:
    st.header("Filtros")
    # Intervalo de datas automático
    if "Data da Venda" in df.columns and df["Data da Venda"].notna().any():
        data_min = pd.to_datetime(df["Data da Venda"]).min()
        data_max = pd.to_datetime(df["Data da Venda"]).max()
        intervalo = st.date_input("Período (Data da Venda)", [data_min, data_max])
    else:
        intervalo = []

    filtro_produto = st.multiselect("Produto", options=sorted(df["Produto"].dropna().unique()))
    filtro_marca = st.multiselect("Marca", options=sorted(df["Marca"].dropna().unique()))
    filtro_loja = st.multiselect("Loja", options=sorted(df["Loja"].dropna().unique()))
    filtro_categoria = st.multiselect("Categoria", options=sorted(df["Categoria"].dropna().unique()))

# Aplicação dos filtros
df_filtrado = df.copy()

if intervalo:
    if len(intervalo) == 2:
        inicio, fim = pd.to_datetime(intervalo[0]), pd.to_datetime(intervalo[1])
        df_filtrado = df_filtrado[(df_filtrado["Data da Venda"] >= inicio) & (df_filtrado["Data da Venda"] <= fim)]
    elif len(intervalo) == 1:
        unico = pd.to_datetime(intervalo[0])
        df_filtrado = df_filtrado[df_filtrado["Data da Venda"] == unico]

if filtro_produto:
    df_filtrado = df_filtrado[df_filtrado["Produto"].isin(filtro_produto)]
if filtro_marca:
    df_filtrado = df_filtrado[df_filtrado["Marca"].isin(filtro_marca)]
if filtro_loja:
    df_filtrado = df_filtrado[df_filtrado["Loja"].isin(filtro_loja)]
if filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(filtro_categoria)]


# KPIs

faturamento_total = pd.to_numeric(df_filtrado.get("Faturamento", pd.Series(dtype=float)), errors="coerce").sum()
qtd_total = pd.to_numeric(df_filtrado.get("Qtd Vendida", pd.Series(dtype="Int64")), errors="coerce").sum()
ticket_medio = (faturamento_total / qtd_total) if (qtd_total and pd.notna(qtd_total) and qtd_total != 0) else 0
total_vendas = len(df_filtrado)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
col2.metric("📦 Qtd Total Vendida", f"{int(qtd_total) if pd.notna(qtd_total) else 0}")
col3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col4.metric("🛒 Total de Vendas", int(total_vendas))

st.divider()

# Gráficos

# 1) Faturamento por mês
if "Data da Venda" in df_filtrado.columns:
    df_mes = (
        df_filtrado
        .set_index("Data da Venda")
        .groupby(pd.Grouper(freq="M"))[["Faturamento"]]
        .sum()
        .reset_index()
    )
    graf1 = px.bar(df_mes, x="Data da Venda", y="Faturamento", title="Faturamento por Mês")
else:
    graf1 = px.bar(title="Faturamento por Mês (dados indisponíveis)")

# 2) Faturamento por loja
if "Loja" in df_filtrado.columns and "Faturamento" in df_filtrado.columns:
    df_loja = df_filtrado.groupby("Loja", as_index=False)["Faturamento"].sum()
    graf2 = px.bar(df_loja, x="Loja", y="Faturamento", title="Faturamento por Loja")
else:
    graf2 = px.bar(title="Faturamento por Loja (dados indisponíveis)")

# 3) Faturamento por Tipo Loja
if "Tipo Loja" in df_filtrado.columns and "Faturamento" in df_filtrado.columns:
    df_tipo = df_filtrado.groupby("Tipo Loja", as_index=False)["Faturamento"].sum()
    graf3 = px.pie(df_tipo, names="Tipo Loja", values="Faturamento", title="Faturamento por Tipo de Loja")
else:
    graf3 = px.pie(title="Faturamento por Tipo de Loja (dados indisponíveis)")

# 4) Quantidade vendida por Marca
if "Marca" in df_filtrado.columns and "Qtd Vendida" in df_filtrado.columns:
    df_marca = df_filtrado.groupby("Marca", as_index=False)["Qtd Vendida"].sum()
    graf4 = px.bar(df_marca, x="Marca", y="Qtd Vendida", title="Qtd Vendida por Marca")
else:
    graf4 = px.bar(title="Qtd Vendida por Marca (dados indisponíveis)")

# Layout dos gráficos
c1, c2 = st.columns(2)
c1.plotly_chart(graf1, use_container_width=True)
c2.plotly_chart(graf2, use_container_width=True)

c3, c4 = st.columns(2)
c3.plotly_chart(graf3, use_container_width=True)
c4.plotly_chart(graf4, use_container_width=True)

st.divider()

# Download dos dados filtrados
csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Baixar dados filtrados (CSV)", data=csv, file_name="dados_filtrados.csv", mime="text/csv")

st.caption("Dica: use os filtros na barra lateral para segmentar por período, loja, produto, marca e categoria.")



st.markdown("---")  
st.markdown(
    "<p style='text-align:center; color:white; font-size:14px;'>Desenvolvido por Tatiana Kami — Desenvolvedora Python & Analista de Dados</p>",
    unsafe_allow_html=True
)

