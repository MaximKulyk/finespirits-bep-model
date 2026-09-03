import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Настройка красивой темы для графиков
sns.set_theme(style='whitegrid', palette='colorblind')

# Конфигурация веб-страницы
st.set_page_config(page_title="FineSpirits BEP Model", layout="wide")

st.title("📊 Интерактивный финансовый симулятор FineSpirits")
st.markdown("Используйте этот симулятор на встрече с Филиппом, чтобы наглядно показать, как структура затрат влияет на выживание бизнеса.")

# ==============================================================================
# БОКОВАЯ ПАНЕЛЬ С НАСТРОЙКАМИ И ВЫБОРОМ СЦЕНАРИЕВ
# ==============================================================================
st.sidebar.header("⚙️ Стратегические сценарии")

# Выбор сценария
scenario = st.sidebar.selectbox(
    "Выберите сценарий анализа:",
    ["Сценарий 1 (Условно-постоянный OPEX)", "Сценарий 2 (Реалистичный с переменным OPEX)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Тонкая настройка параметров")

# Интерактивные слайдеры с дефолтными значениями из модели
current_revenue = st.sidebar.slider(
    "Текущая выручка в месяц ($)", 
    min_value=10000, max_value=600000, value=73791, step=5000
)

cogs_pct = st.sidebar.slider(
    "Себестоимость товаров (COGS %)", 
    min_value=40.0, max_value=95.0, value=81.0, step=0.5
) / 100.0

if scenario == "Сценарий 1 (Условно-постоянный OPEX)":
    # В Сценарии 1 вся сумма OPEX ($82,217) условно-постоянная, логистика не выделяется отдельно
    fixed_costs = st.sidebar.slider(
        "Постоянный OPEX в месяц ($)", 
        min_value=10000, max_value=150000, value=82217, step=1000
    )
    logistic_pct = 0.0
else:
    # В Сценарии 2 часть OPEX постоянная ($59,717), а логистика ($22,500) становится переменной (30.5%)
    fixed_costs = st.sidebar.slider(
        "Постоянный OPEX в месяц ($)", 
        min_value=10000, max_value=150000, value=59717, step=1000
    )
    logistic_pct = st.sidebar.slider(
        "Доля переменных OPEX (Логистика %)", 
        min_value=0.0, max_value=50.0, value=30.5, step=0.5
    ) / 100.0

# ==============================================================================
# МАТЕМАТИЧЕСКИЕ РАСЧЕТЫ
# ==============================================================================
total_variable_pct = cogs_pct + logistic_pct  # Совокупная доля переменных затрат
marginal_profit_pct = 1.0 - total_variable_pct  # Маржинальность (Contribution Margin %)

# Расчет точки безубыточности
if marginal_profit_pct > 0:
    bep_revenue = fixed_costs / marginal_profit_pct
    bep_status = f"${bep_revenue:,.0f}"
else:
    bep_revenue = None
    bep_status = "НЕДОСТИЖИМА (Отрицательный маржинальный доход!)"

# Текущие результаты
current_variable_costs = current_revenue * total_variable_pct
current_profit = current_revenue - current_variable_costs - fixed_costs

# ==============================================================================
# ВЕРХНИЕ СВОДНЫЕ ИНДИКАТОРЫ (METRICS)
# ==============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Выручка", f"${current_revenue:,.0f}")
with col2:
    st.metric("Переменные расходы (Всего %)", f"{total_variable_pct*100:.1f}%")
with col3:
    st.metric("Точка безубыточности (ВЕР)", bep_status)
with col4:
    st.metric(
        "Чистая прибыль / Убыток", 
        f"${current_profit:,.0f}", 
        delta=f"Маржинальность: {marginal_profit_pct*100:.1f}%",
        delta_color="normal" if current_profit >= 0 else "inverse"
    )

st.markdown("---")

# ==============================================================================
# ВИЗУАЛИЗАЦИЯ (ПОСТРОЕНИЕ ГРАФИКА)
# ==============================================================================
col_graph, col_text = st.columns([2, 1])

with col_graph:
    x_revenue = np.linspace(0, 600000, 1000)
    revenue_line = x_revenue
    total_costs_line = fixed_costs + total_variable_pct * x_revenue

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_revenue, revenue_line, label='Выручка (Sales)', color='#1a73e8', linewidth=2.5)
    ax.plot(x_revenue, total_costs_line, label='Совокупные затраты (Total Costs)', 
            color='#d93025' if total_variable_pct >= 1.0 else '#5f6368', linewidth=2.5)
    ax.axhline(y=fixed_costs, label='Постоянные расходы (Fixed Costs)', color='#9aa0a6', linestyle='--', linewidth=1.5)

    # Заливка зон прибыли и убытка
    if total_variable_pct < 1.0:
        ax.fill_between(x_revenue, revenue_line, total_costs_line, 
                        where=(total_costs_line > revenue_line), color='#fce8e6', alpha=0.6, label='Убыток (Loss)')
        ax.fill_between(x_revenue, revenue_line, total_costs_line, 
                        where=(revenue_line > total_costs_line), color='#e6f4ea', alpha=0.6, label='Прибыль (Profit)')
    else:
        ax.fill_between(x_revenue, revenue_line, total_costs_line, color='#fce8e6', alpha=0.6, label='Убыток (Loss)')

    # Нанесение точек ВЕР и Текущего состояния
    if bep_revenue and bep_revenue <= 600000:
        ax.plot(bep_revenue, bep_revenue, 'o', color='#1a73e8', markersize=8)
        ax.annotate(f'ВЕР: ${bep_revenue:,.0f}', xy=(bep_revenue, bep_revenue), 
                    xytext=(bep_revenue - 110000, bep_revenue + 30000),
                    arrowprops=dict(facecolor='black', arrowstyle='->', lw=0.8), fontsize=10, fontweight='bold')

    current_total_costs = fixed_costs + total_variable_pct * current_revenue
    ax.plot(current_revenue, current_total_costs, 'x', color='#d93025' if current_profit < 0 else '#1e8e3e', markersize=9, markeredgewidth=2.5)

    ax.set_xlabel('Выручка (USD)', fontsize=10)
    ax.set_ylabel('Сумма (USD)', fontsize=10)
    ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left')
    sns.despine()

    st.pyplot(fig)

with col_text:
    st.subheader("💡 Аналитическая записка")

    if scenario == "Сценарий 1 (Условно-постоянный OPEX)":
        st.info(
            f"**Выводы по Сценарию 1:**\\n\\n"
            f"Если принять, что все операционные расходы компании постоянные, то чтобы покрыть затраты в **${fixed_costs:,.0f}** при маржинальности в **{(1-cogs_pct)*100:.1f}%**, "
            f"компании необходима выручка в размере **{bep_status}** в месяц.\\n\\n"
            f"Это требует роста текущих продаж в **{bep_revenue/current_revenue:.1f} раз(а)**. "
            f"Подобный сценарий малореалистичен без кратного расширения инфраструктуры."
        )
    else:
        if total_variable_pct >= 1.0:
            st.error(
                f"**КРИТИЧЕСКИЙ РИСК (Сценарий 2):**\\n\\n"
                f"Так как переменные затраты составляют **{total_variable_pct*100:.1f}%** от цены (превышают 100%), "
                f"компания генерирует убыток с каждой проданной бутылки.\\n\\n"
                f"**Точка безубыточности физически недостижима!** Масштабирование текущих продаж без пересмотра условий с поставщиками (COGS) или тарифов на логистику будет только быстрее истощать оборотный капитал."
            )
        else:
            st.warning(
                f"**Анализ Сценария 2 (Оптимизированный):**\\n\\n"
                f"При снижении совокупной доли переменных затрат до **{total_variable_pct*100:.1f}%** (за счет снижения закупки или оптимизации доставки), "
                f"маржинальность становится положительной: **{marginal_profit_pct*100:.1f}%**.\\n\\n"
                f"Теперь точка безубыточности составляет **{bep_status}** в месяц. Это реальная цель для обсуждения совместного плана действий."
            )
