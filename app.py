import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройка страницы
st.set_page_config(
    page_title="FineSpirits BEP Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилизация под бренд (Burgundy & Gold) через Markdown
st.markdown("""
    <style>
    .main { background-color: #FAF9F6; }
    h1 { color: #6B1D2F; font-family: 'Georgia', serif; }
    h2, h3 { color: #2B2B2B; font-family: 'Georgia', serif; }
    .stButton>button {
        background-color: #6B1D2F;
        color: #FAF9F6;
        border-radius: 5px;
        border: 1px solid #C5A059;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #C5A059;
        color: #6B1D2F;
    }
    .metric-box {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #C5A059;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-title { font-size: 14px; color: #7F8C8D; font-weight: bold; }
    .metric-value { font-size: 24px; color: #2C3E50; font-weight: bold; }
    .metric-value-negative { font-size: 24px; color: #C0392B; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Заголовок
st.title("🍷 Интерактивный симулятор юнит-экономики FineSpirits")
st.markdown("### Анализ точки безубыточности и симуляция сценариев оптимизации (YTD 2026)")
st.write("---")

# Инициализация сессии для пресетов
if 'preset' not in st.session_state:
    st.session_state.preset = 'current'

# Боковая панель
st.sidebar.header("🛠️ Управление сценариями")

# Кнопки быстрых пресетов
col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("📉 Текущий YTD"):
    st.session_state.preset = 'current'
if col_btn2.button("🚀 Оптимальный"):
    st.session_state.preset = 'target'

# Установка значений ползунков в зависимости от выбранного пресета
if st.session_state.preset == 'current':
    default_rev = 98386.0
    default_cogs = 85.8
    default_v_opex = 16.4
    default_f_opex = 48083.0
else:
    default_rev = 267126.0
    default_cogs = 70.0
    default_v_opex = 12.0
    default_f_opex = 48083.0

st.sidebar.markdown("---")
st.sidebar.markdown("### Регулировка параметров")

# Слайдеры
revenue = st.sidebar.slider(
    "Ежемесячная выручка (Sales), USD", 
    min_value=0, max_value=500000, 
    value=int(default_rev), step=5000
)

cogs_pct = st.sidebar.slider(
    "Себестоимость товаров (COGS), %", 
    min_value=40.0, max_value=100.0, 
    value=float(default_cogs), step=0.5
)

v_opex_pct = st.sidebar.slider(
    "Переменная логистика/доставка, %", 
    min_value=5.0, max_value=30.0, 
    value=float(default_v_opex), step=0.1
)

fixed_costs = st.sidebar.slider(
    "Постоянные расходы (Fixed OPEX), USD", 
    min_value=10000, max_value=80000, 
    value=int(default_f_opex), step=500
)

# Расчеты юнит-экономики
total_var_pct = cogs_pct + v_opex_pct
contribution_margin_pct = 100.0 - total_var_pct
contribution_margin_usd = revenue * (contribution_margin_pct / 100.0)
net_profit = contribution_margin_usd - fixed_costs

# Точка безубыточности (ВЕР)
if contribution_margin_pct > 0:
    bep_revenue = fixed_costs / (contribution_margin_pct / 100.0)
    bep_status = f"${bep_revenue:,.0f}"
    growth_needed = bep_revenue / 98386.54
    growth_status = f"{growth_needed:.2f}x"
else:
    bep_revenue = None
    bep_status = "НЕДОСТИЖИМА"
    growth_status = "—"

# Верхняя панель KPI на основном экране
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">МАРЖИНАЛЬНОСТЬ (CM %)</div>
            <div class="{"metric-value" if contribution_margin_pct > 0 else "metric-value-negative"}">
                {contribution_margin_pct:.1f}%
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">ЧИСТАЯ ПРИБЫЛЬ / (УБЫТОК)</div>
            <div class="{"metric-value" if net_profit >= 0 else "metric-value-negative"}">
                ${net_profit:,.0f}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">ТОЧКА БЕЗУБЫТОЧНОСТИ</div>
            <div class="{"metric-value" if bep_revenue else "metric-value-negative"}">
                {bep_status}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">ТРЕБУЕМЫЙ РОСТ ПРОДАЖ</div>
            <div class="metric-value">{growth_status}</div>
        </div>
    """, unsafe_allow_html=True)

# Основная рабочая область: график и пояснения
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 📊 Интерактивная траектория прибыли")
    
    # Построение графика безубыточности
    x_range = np.linspace(0, 500000, 100)
    rev_line = x_range
    costs_line = fixed_costs + (total_var_pct / 100.0) * x_range
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor('#FAF9F6')
    ax.set_facecolor('#FFFFFF')
    
    # Линии
    ax.plot(x_range, rev_line, label="Выручка (Sales)", color="#1F4E78", linewidth=2.5)
    ax.plot(x_range, costs_line, label="Совокупные расходы", color="#6B1D2F", linewidth=2.5)
    ax.axhline(y=fixed_costs, label="Постоянные расходы", color="#7F8C8D", linestyle="--", linewidth=1.5)
    
    # Области прибыли и убытка
    if contribution_margin_pct > 0:
        ax.fill_between(x_range, rev_line, costs_line, where=(rev_line > costs_line), color='#E2EFDA', alpha=0.6, label="Прибыль")
        ax.fill_between(x_range, rev_line, costs_line, where=(rev_line <= costs_line), color='#FCE8E6', alpha=0.6, label="Убыток")
    else:
        ax.fill_between(x_range, rev_line, costs_line, color='#FCE8E6', alpha=0.6, label="Убыток")
        
    # Точки текущего положения и безубыточности
    ax.plot(revenue, revenue * (total_var_pct / 100.0) + fixed_costs, 'o', color="#C5A059", markersize=10, label="Текущий выбор")
    
    if bep_revenue and bep_revenue <= 500000:
        ax.plot(bep_revenue, bep_revenue, 'o', color="#27AE60", markersize=10, label="Точка BEP")
        
    # Форматирование осей
    ax.set_xlim(0, 500000)
    ax.set_ylim(0, 500000)
    ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.set_xlabel("Выручка (USD)", fontsize=10, color="#2B2B2B")
    ax.set_ylabel("Сумма (USD)", fontsize=10, color="#2B2B2B")
    ax.legend(loc="upper left", frameon=True, facecolor="#FFFFFF")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#BDC3C7')
    ax.spines['bottom'].set_color('#BDC3C7')
    ax.grid(True, linestyle=":", alpha=0.6, color="#BDC3C7")
    
    st.pyplot(fig)

with col_right:
    st.markdown("### 🔍 Аналитический диагноз")
    
    if contribution_margin_pct <= 0:
        st.error(f"""
        **КРИТИЧЕСКИЙ РИСК:**  
        Маржинальная рентабельность бизнеса отрицательная (**{contribution_margin_pct:.1f}%**).  
        
        Это означает, что на каждом проданном литре алкоголя компания генерирует убыток. Увеличение продаж при таких параметрах **не выведет бизнес в плюс**, а только увеличит совокупную дыру в бюджете. 
        
        *Необходимо срочно снижать закупку (COGS) или логистические издержки.*
        """)
    else:
        st.success(f"""
        **БИЗНЕС-МОДЕЛЬ СТАБИЛЬНА:**  
        Каждый доллар выручки приносит **{contribution_margin_pct:.1f} центов** маржинального дохода.
        
        При текущих параметрах, чтобы покрыть постоянные расходы в размере **${fixed_costs:,.0f}**, вам необходимо выйти на объем продаж **${bep_revenue:,.0f}** в месяц. 
        
        Любая продажа сверх этого лимита уходит напрямую в чистую прибыль компании.
        """)
        
    st.markdown("""
    ### 💡 Ключевые выводы для Филиппа:
    1. **Зависимость от COGS:** Снижение себестоимости закупки всего на **5%** снижает планку безубыточности более чем на **$65,000** в месяц.
    2. **Логистический рычаг:** Оптимизация контрактов доставки с InPost/DPD позволяет высвободить критически важный оборотный капитал.
    3. **Вычленение НДС:** Отказ от переплат НДС польским поставщикам позволяет удерживать фиксированные расходы на уровне **$48,083** без вреда для операционной деятельности.
    """)
    
    st.info("💡 *Нажмите кнопку **🚀 Оптимальный** в левом меню, чтобы мгновенно показать целевой план выхода на безубыточность, утвержденный акционерами.*")
