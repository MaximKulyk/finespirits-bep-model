import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Настройка страницы под мобильные и ПК
st.set_page_config(
    page_title="FineSpirits Simulator v8.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Премиальная стилизация бренда (Burgundy & Gold)
st.markdown("""
    <style>
    .main { background-color: #FAF9F6; }
    h1 { color: #6B1D2F; font-family: 'Georgia', serif; font-weight: bold; }
    h2, h3 { color: #2B2B2B; font-family: 'Georgia', serif; }
    .stCheckbox>label { font-weight: bold; color: #2C3E50; }
    .stButton>button {
        background-color: #6B1D2F;
        color: #FAF9F6;
        border-radius: 5px;
        border: 1px solid #C5A059;
        font-weight: bold;
        width: 100%;
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        text-align: center;
    }
    .metric-title { font-size: 12px; color: #7F8C8D; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 26px; color: #1F4E78; font-weight: bold; }
    .metric-value-negative { font-size: 26px; color: #9C0006; font-weight: bold; }
    .status-badge {
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Хедер
st.title("🍷 Интерактивный симулятор FineSpirits v8.0 (Без иллюзий)")
st.markdown("##### Моделирование 11 пунктов оптимизации, дебиторской задолженности и окупаемости за 12 месяцев")
st.write("---")

# Инициализация состояния
if 'preset' not in st.session_state:
    st.session_state.preset = 'current'

# --- БОКОВАЯ ПАНЕЛЬ: ТУМБЛЕРЫ 11 ПУНКТОВ ---
st.sidebar.markdown("## 🛠️ СЦЕНАРИИ И ПРЕСЕТЫ")
col_b1, col_btn2 = st.sidebar.columns(2)
if col_b1.button("📉 Текущий YTD"):
    st.session_state.preset = 'current'
if col_btn2.button("🚀 План v7/v8"):
    st.session_state.preset = 'target'

st.sidebar.write("---")
st.sidebar.markdown("## 🛑 КОНТРОЛЬ ПОСТОЯННЫХ ЗАТРАТ")

# Динамический расчет Fixed OPEX на основе тумблеров
if st.session_state.preset == 'current':
    shop_closed = False
    fot_optimized = False
    leasing_cars = 3
    soft_optimized = False
    vat_recovered = False
    cogs_val = 85.8
    v_opex_val = 16.4
    sales_growth = 2.0
    debt_recovery = 0
else:
    shop_closed = True
    fot_optimized = True
    leasing_cars = 1
    soft_optimized = True
    vat_recovered = True
    cogs_val = 70.0
    v_opex_val = 15.0
    sales_growth = 10.0
    debt_recovery = 80000

# Интерактивные тумблеры кост-киллинга
shop_closed = st.sidebar.checkbox("1. Закрыть офлайн-магазин (Экономия $10,000/мес)", value=shop_closed)
fot_optimized = st.sidebar.checkbox("2. Срезать ФОТ на 33% (Экономия $10,000/мес)", value=fot_optimized)
leasing_cars = st.sidebar.slider("🚗 Лизинг автомобилей (машин)", 1, 3, value=leasing_cars)
soft_optimized = st.sidebar.checkbox("3-4. Мораторий на софт и FB-маркетинг (Экономия $7,000/мес)", value=soft_optimized)
vat_recovered = st.sidebar.checkbox("🏛️ Вычленение НДС 23% польских счетов (Экономия $4,258/мес)", value=vat_recovered)

# Расчет Fixed OPEX на лету
base_fixed = 48083
if shop_closed: base_fixed -= 10000
if fot_optimized: base_fixed -= 10000
if soft_optimized: base_fixed -= 7000
if vat_recovered: base_fixed -= 4258
# Лизинг машин: каждая лишняя машина сверх 1 стоит $1,500/мес
base_fixed -= (3 - leasing_cars) * 1500

fixed_costs = max(10000, base_fixed) # Страховка от ухода ниже минимума

st.sidebar.write("---")
st.sidebar.markdown("## 📈 ПЕРЕМЕННЫЕ ЗАТРАТЫ И РОСТ")
cogs_pct = st.sidebar.slider("Себестоимость товаров (COGS), %", 45.0, 100.0, float(cogs_val), 0.5)
v_opex_pct = st.sidebar.slider("Переменная логистика (InPost/DPD), %", 5.0, 30.0, float(v_opex_val), 0.5)
growth_pct = st.sidebar.slider("Ежемесячный темп роста продаж, %", 0.0, 20.0, float(sales_growth), 0.5)

st.sidebar.write("---")
st.sidebar.markdown("## 💰 ДЕБИТОРКА И ОБОРОТНЫЙ КАПИТАЛ")
debt_recovery = st.sidebar.slider("Возврат дебиторской задолженности (PLN)", 0, 130000, int(debt_recovery), 10000)
debt_usd = debt_recovery / 3.67 # Конвертация по курсу

# --- РАСЧЕТЫ ---
total_var_pct = cogs_pct + v_opex_pct
contribution_margin_pct = 100.0 - total_var_pct
starting_revenue = 98386.0

# Прогноз за 12 месяцев
months = [f"M{i}" for i in range(1, 13)]
rev_proj = []
profit_proj = []
cum_cash_needed = []
running_rev = starting_revenue
cumulative = 0

for i in range(12):
    rev_proj.append(running_rev)
    cm_usd = running_rev * (contribution_margin_pct / 100.0)
    net_p = cm_usd - fixed_costs
    profit_proj.append(net_p)
    
    # Вливание кэша в этом месяце
    cash_infusion = -net_p if net_p < 0 else 0
    
    # Влияние возврата дебиторки (PLN -> USD) в первые два месяца
    if i == 0 and debt_usd > 0:
        cash_infusion = max(0, cash_infusion - (debt_usd / 2))
    elif i == 1 and debt_usd > 0:
        cash_infusion = max(0, cash_infusion - (debt_usd / 2))
        
    cumulative += cash_infusion
    cum_cash_needed.append(cumulative)
    running_rev *= (1 + (growth_pct / 100.0))

# Точка безубыточности (ВЕР)
if contribution_margin_pct > 0:
    bep_revenue = fixed_costs / (contribution_margin_pct / 100.0)
    bep_status = f"${bep_revenue:,.0f}"
    growth_needed = bep_revenue / starting_revenue
    growth_status = f"{growth_needed:.2f}x"
else:
    bep_revenue = None
    bep_status = "НЕДОСТИЖИМА"
    growth_status = "—"

current_profit = (starting_revenue * (contribution_margin_pct / 100.0)) - fixed_costs

# --- ПАНЕЛЬ KPI ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Текущие постоянные расходы (Fixed)</div><div class="metric-value">${fixed_costs:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Маржинальная рентабельность (CM %)</div><div class="{"metric-value" if contribution_margin_pct > 0 else "metric-value-negative"}">{contribution_margin_pct:.1f}%</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Чистый результат (Старт)</div><div class="{"metric-value" if current_profit >= 0 else "metric-value-negative"}">${current_profit:,.0f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Точка безубыточности (BEP)</div><div class="{"metric-value" if bep_revenue else "metric-value-negative"}">{bep_status}</div></div>', unsafe_allow_html=True)

# Светофор статуса бизнес-модели
if contribution_margin_pct <= 0:
    st.markdown('<div class="status-badge" style="background-color: #FCE8E6; color: #9C0006; border: 1px solid #9C0006;">🚨 КРИТИЧЕСКИЙ СТАТУС: Юнит-экономика отрицательная. Каждая продажа приносит убыток! Рост продаж усугубит ситуацию.</div>', unsafe_allow_html=True)
elif bep_revenue and bep_revenue > 250000:
    st.markdown(f'<div class="status-badge" style="background-color: #FFF2CC; color: #B78103; border: 1px solid #B78103;">⚠️ ПРЕДУПРЕЖДЕНИЕ: Модель жизнеспособна, но точка безубыточности ({bep_status}) слишком высока. Требуется рост продаж более чем в {growth_status}.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-badge" style="background-color: #E2EFDA; color: #27AE60; border: 1px solid #27AE60;">✅ СТАБИЛЬНЫЙ СТАТУС: Бизнес-модель оздоровлена! Точка безубыточности ({bep_status}) находится в зоне быстрой достижимости.</div>', unsafe_allow_html=True)

# --- ГРАФИКИ БЕЗУБЫТОЧНОСТИ И ДВИЖЕНИЯ КЭША ---
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.markdown("### 📊 Интерактивный CVP-анализ (График BEP)")
    x_range = np.linspace(0, 500000, 100)
    costs_line = fixed_costs + (total_var_pct / 100.0) * x_range
    
    fig1, ax1 = plt.subplots(figsize=(10, 5.5))
    fig1.patch.set_facecolor('#FAF9F6')
    ax1.set_facecolor('#FFFFFF')
    
    ax1.plot(x_range, x_range, label="Выручка (Sales)", color="#1F4E78", linewidth=2.5)
    ax1.plot(x_range, costs_line, label="Совокупные расходы", color="#6B1D2F", linewidth=2.5)
    ax1.axhline(y=fixed_costs, label="Постоянные расходы (OPEX)", color="#7F8C8D", linestyle="--")
    
    if contribution_margin_pct > 0:
        ax1.fill_between(x_range, x_range, costs_line, where=(x_range > costs_line), color='#E2EFDA', alpha=0.5, label="Зона прибыли")
        ax1.fill_between(x_range, x_range, costs_line, where=(x_range <= costs_line), color='#FCE8E6', alpha=0.5, label="Зона убытка")
    else:
        ax1.fill_between(x_range, x_range, costs_line, color='#FCE8E6', alpha=0.5, label="Зона убытка")
        
    ax1.plot(revenue, revenue * (total_var_pct / 100.0) + fixed_costs, 'o', color="#C5A059", markersize=10, label="Текущая точка")
    if bep_revenue and bep_revenue <= 500000:
        ax1.plot(bep_revenue, bep_revenue, 'o', color="#27AE60", markersize=10, label="Точка BEP")
        
    ax1.set_xlim(0, 500000)
    ax1.set_ylim(0, 500000)
    ax1.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax1.legend(loc="upper left")
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(True, linestyle=":", alpha=0.5)
    st.pyplot(fig1)

with col_graph2:
    st.markdown("### 📅 Кумулятивная потребность в инвестициях (кэш от акционеров)")
    
    fig2, ax2 = plt.subplots(figsize=(10, 5.5))
    fig2.patch.set_facecolor('#FAF9F6')
    ax2.set_facecolor('#FFFFFF')
    
    # Строим график накопленного дефицита денежных средств
    ax2.plot(months, cum_cash_needed, label="Накопленное вливание кэша", color="#6B1D2F", linewidth=3, marker="o")
    ax2.fill_between(months, cum_cash_needed, color="#FCE8E6", alpha=0.4)
    
    ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax2.set_title("Общая потребность в финансировании на разгоне продаж", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Суммарный объем вливаний акционеров", fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # Подпись пикового значения
    peak_val = max(cum_cash_needed)
    peak_month = months[cum_cash_needed.index(peak_val)]
    if peak_val > 0:
        ax2.annotate(f"Пик финансирования: ${peak_val:,.0f}", 
                     xy=(peak_month, peak_val), 
                     xytext=(peak_month, peak_val * 0.7 if peak_val * 0.7 > 10000 else peak_val + 5000),
                     arrowprops=dict(facecolor='black', arrowstyle='->', lw=0.8),
                     fontsize=9, fontweight='bold', color="#9C0006")
                     
    st.pyplot(fig2)

# --- АНАЛИТИЧЕСКИЙ БЛОК ОКУПАЕМОСТИ ---
st.markdown("### 📋 Динамический 12-месячный план-прогноз")
cols_months = st.columns(6)

# Находим месяц окупаемости
break_even_month = "Не достигается за 12 мес"
for m_idx, prof in enumerate(profit_proj):
    if prof >= 0:
        break_even_month = f"Месяц M{m_idx+1}"
        break

for i in range(6):
    with cols_months[i]:
        st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 10px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border-top: 3px solid #6B1D2F; text-align: center; margin-bottom: 10px;">
                <div style="font-size: 11px; color: #7F8C8D; font-weight: bold;">M{i+1} ({'Авг' if i==0 else 'Сен' if i==1 else 'Окт' if i==2 else 'Ноя' if i==3 else 'Дек' if i==4 else 'Янв'})</div>
                <div style="font-size: 11px; margin-top: 5px;">Выручка: <b>${rev_proj[i]:,.0f}</b></div>
                <div style="font-size: 11px; color: {'#27AE60' if profit_proj[i]>=0 else '#9C0006'}">Прибыль: <b>${profit_proj[i]:,.0f}</b></div>
                <div style="font-size: 10px; color: #7F8C8D; margin-top: 3px;">Кэш-нужда: ${cum_cash_needed[i]:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

cols_months_2 = st.columns(6)
for i in range(6, 12):
    with cols_months_2[i-6]:
        st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 10px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border-top: 3px solid #6B1D2F; text-align: center; margin-bottom: 10px;">
                <div style="font-size: 11px; color: #7F8C8D; font-weight: bold;">M{i+1} ({'Фев' if i==6 else 'Мар' if i==7 else 'Апр' if i==8 else 'Май' if i==9 else 'Июн' if i==10 else 'Июл'})</div>
                <div style="font-size: 11px; margin-top: 5px;">Выручка: <b>${rev_proj[i]:,.0f}</b></div>
                <div style="font-size: 11px; color: {'#27AE60' if profit_proj[i]>=0 else '#9C0006'}">Прибыль: <b>${profit_proj[i]:,.0f}</b></div>
                <div style="font-size: 10px; color: #7F8C8D; margin-top: 3px;">Кэш-нужда: ${cum_cash_needed[i]:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

st.write("---")
col_summary_1, col_summary_2 = st.columns(2)
with col_summary_1:
    st.markdown(f"**⏱️ Срок выхода на самоокупаемость (прибыль $\ge$ \$0):** `{break_even_month}`")
    st.markdown(f"**💰 Максимальная потребность в инвестициях (Пик кэш-нужды):** `${max(cum_cash_needed):,.0f}`")
with col_summary_2:
    st.markdown(f"**🏛️ Высвобождение оборотного капитала за счет дебиторки:** `+{debt_recovery:,.0f} PLN` (~${debt_usd:,.0f} USD)")
    st.markdown(f"**🍇 Итоговая чистая прибыль на M12 (Июль 2027 г.):** `${profit_proj[-1]:,.0f}`")
