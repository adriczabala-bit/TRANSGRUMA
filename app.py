import base64, json, html
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "transgruma_data.json").read_text(encoding="utf-8"))

st.set_page_config(page_title="Transgruma · Calculadora de presupuestos", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

NAVY = "#0A2342"
GREEN = "#1B8A4B"
PALE = "#E6F4EC"
MUTED = "#5B6B7C"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: Inter, 'Segoe UI', sans-serif; }}
.stApp {{ background: #F3F6F9; color: #10243A; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1rem; max-width: 1500px; }}
.topbar {{background:{NAVY}; color:#fff; padding:14px 20px; border-bottom:4px solid {GREEN}; border-radius:10px; display:flex; align-items:center; gap:15px; margin-bottom:12px;}}
.topbar img {{height:42px; width:auto; background:white; border-radius:6px; padding:4px 8px;}}
.topbar .slogan {{font-weight:700; font-size:16px;}}
.topbar .prices {{margin-left:auto; opacity:.9; font-size:13px;}}
.hero {{background:linear-gradient(120deg,{NAVY} 55%,#0f3a52); color:white; padding:26px 28px; border-radius:12px; margin:0 0 20px 0;}}
.hero h1 {{font-size:clamp(28px,3vw,43px); line-height:1.12; margin:0; color:white; font-weight:800;}}
.hero h1 em {{color:#5fd08f; font-style:normal;}}
.hero p {{color:#e5edf5; margin:10px 0 0; max-width:760px;}}
.section {{background:white; border:1px solid #D5DEE8; border-radius:12px; padding:18px 20px 10px; margin-bottom:16px;}}
.section-title {{font-weight:750; font-size:18px; margin:0 0 14px; display:flex; gap:10px; align-items:center; color:{NAVY};}}
.num {{background:{GREEN}; color:white; width:27px; height:27px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:13px;}}
.machine-img {{height:74px; width:100%; object-fit:contain;}}
.machine-caption {{font-size:12px; color:{MUTED}; text-align:center; min-height:32px;}}
div.stButton > button {{border-radius:10px; border:1px solid #D5DEE8; font-weight:650; min-height:45px;}}
div.stButton > button[kind="primary"] {{background:{GREEN}; border-color:{GREEN}; color:white;}}
div[data-testid="stMetric"] {{background:white; border:1px solid #D5DEE8; padding:12px 14px; border-radius:10px;}}
.summary-head {{background:{NAVY}; color:white; padding:15px; text-align:center; border-radius:10px 10px 0 0;}}
.summary-total {{background:{PALE}; border-radius:10px; padding:15px;}}
.small-muted {{font-size:12px;color:{MUTED};}}
hr {{border-color:#D5DEE8;}}
footer {{visibility:hidden;}}
</style>
""", unsafe_allow_html=True)

def img_bytes(key):
    return (ROOT / "assets" / f"{key}.webp").read_bytes()

def euro(n):
    return (f"{n:,.2f} €").replace(',', 'X').replace('.', ',').replace('X', '.')

def number(label, key, default=0.0, min_value=0.0, step=1.0, help=None):
    return st.number_input(label, min_value=min_value, value=float(default), step=float(step), key=key, help=help)

def checkbox(label, key, value=False):
    return st.checkbox(label, value=value, key=key)

GROUPS = {
    'mini': ('Minigrúas araña', '2 a 15 t'),
    'cam': ('Camiones grúa y transporte', '50 a 180 t·m'),
    'tel': ('Grúas telescópicas', '40 a 350 t'),
    'pemp': ('PEMP sobre camión', '20 a 90 m'),
    'pn': ('Pasarelas PEMP-N', '7 a 19 m'),
    'bomba': ('Bombas de hormigón', '24 a 67 m'),
}
MODES = {'sc':'Servicio corto (salida + horas mínimas)', 'd':'Por días', 'w':'Por semanas', 'm':'Por meses'}
UNITS = {'d':'día(s)', 'w':'semana(s)', 'm':'mes(es)'}

# Header and slogan
logo64 = base64.b64encode(img_bytes('logo')).decode()
st.markdown(f"""<div class="topbar"><img src="data:image/webp;base64,{logo64}" alt="Transgruma"><span class="slogan">Elevando su confianza</span><span class="prices">Precios Netos 2024</span></div><div class="hero"><h1>Presupuesta tu alquiler,<br><em>elevando su confianza</em></h1><p>Calcula al instante el coste de grúas, plataformas y bombas de hormigón con las tarifas del catálogo Precios Netos 2024.</p></div>""", unsafe_allow_html=True)

if 'group' not in st.session_state: st.session_state.group = 'tel'

# Machine family selection
st.markdown('<div class="section-title"><span class="num">1</span>Tipo de maquinaria</div>', unsafe_allow_html=True)
cols = st.columns(6)
for col, (key, (title, subtitle)) in zip(cols, GROUPS.items()):
    with col:
        st.image(img_bytes(key), use_container_width=True)
        st.markdown(f'<div class="machine-caption"><b>{html.escape(title)}</b><br>{html.escape(subtitle)}</div>', unsafe_allow_html=True)
        if st.button('Seleccionada ✓' if st.session_state.group == key else 'Seleccionar', key=f'pick_{key}', type='primary' if st.session_state.group == key else 'secondary', use_container_width=True):
            st.session_state.group = key
            st.rerun()

g = st.session_state.group
machines = [e for e in DATA['EQ'] if e['g'] == g]
if not machines:
    st.error('No hay modelos cargados para esta familia.')
    st.stop()

# Model and pricing selection
st.markdown('<div class="section-title"><span class="num">2</span>Modelo y modalidad</div>', unsafe_allow_html=True)
c1,c2,c3 = st.columns([2,1.3,1.4])
with c1:
    options = {f"{e['m']}{' · '+e['cap'] if e.get('cap') else ''}": e['id'] for e in machines}
    selected_label = st.selectbox('Modelo', list(options.keys()), key=f'model_{g}')
    model_id = options[selected_label]
with c2:
    season = 'Todo el año'
    if g == 'pemp': season = st.selectbox('Temporada', ['Baja (nov–may)', 'Alta (jun–oct)'], key='season')
with c3:
    p = DATA['PR'][model_id][season if season in DATA['PR'][model_id] else 'Todo el año']
    mode = 'd'
    if g != 'bomba':
        available = [k for k in MODES if (k == 'sc' and 'sm' in p) or k in p]
        default_mode = 'd' if 'd' in available else available[0]
        mode = st.selectbox('Modalidad de alquiler', available, index=available.index(default_mode), format_func=lambda k: MODES[k], key=f'mode_{model_id}_{season}')

L = []
def add(title, amount, note=''):
    if amount > 0.004:
        L.append((title, float(amount), note))

# Shared inputs
if g != 'bomba':
    if mode != 'sc':
        n = number('Cantidad (días, semanas o meses)', 'quantity', 1, min_value=1, step=1)
    else:
        n = 1
    pern = checkbox('La máquina pernocta en obra (la salida se factura solo el primer día)', 'pernocta', True)
    st.markdown('<div class="section-title"><span class="num">3</span>Horario y horas</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a: h0 = number('Horas adicionales en horario normal (L-V 8-17 h)', 'h0', 0)
    with b: h1 = number('Horas extra L-V 6-8 h y 17-22 h', 'h1', 0)
    with c: h2 = number('Horas en sábado, domingo, festivo o nocturno', 'h2', 0)
else:
    n, pern, h0, h1, h2 = 1, True, 0, 0, 0

if g == 'bomba':
    st.markdown('<div class="section-title"><span class="num">3</span>Servicio de bombeo</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a: m3 = number('Hormigón a bombear al día (m³)', 'm3', 80)
    with b: hb = number('Horas de bombeo (si son 55 m³ o menos)', 'hb', 3)
    with c: tub = st.selectbox('Servicio de tubería', [0,0.5,1,2], format_func=lambda x:{0:'Sin tubería',0.5:'Hasta 100 m (+50 %)',1:'De 101 a 150 m (+100 %)',2:'De 151 a 200 m (+200 %)'}[x], key='tub')
    a,b,c = st.columns(3)
    with a: hd = number('Horas a disposición por bajo rendimiento', 'hd', 0)
    with b: b18 = number('Horas extra L-V 18-22 h', 'b18', 0)
    with c: b22 = number('Horas nocturnas, sábados o festivos', 'b22', 0)
    bop = number('Horas de operario especializado (estático)', 'bop', 0)
else:
    m3,hb,tub,hd,b18,b22,bop = 0,0,0,0,0,0,0

st.markdown('<div class="section-title"><span class="num">4</span>Desplazamiento y personal</div>', unsafe_allow_html=True)
a,b,c = st.columns(3)
with a: km = number('Distancia a la obra desde Leganés (km, un sentido)', 'km', 20)
if g != 'bomba':
    with b: ah = number('Ayudante de gruista (horas)', 'ah', 0)
    with c: prov = st.selectbox('Ámbito del ayudante', [1,0], format_func=lambda x: 'Dentro de la provincia (42,80 €/h)' if x==1 else 'Fuera de la provincia (53,50 €/h)', key='prov')
    dt = number('Dirección técnica (horas)', 'dt', 0)
    if g == 'pemp': o2 = checkbox('Segundo operador auxiliar a petición del cliente (8 h/día)', 'o2', False)
    else: o2 = False
else:
    ah,prov,dt,o2 = 0,1,0,False

st.markdown('<div class="section-title"><span class="num">5</span>Gastos y servicios adicionales</div>', unsafe_allow_html=True)
a,b,c = st.columns(3)
with a:
    plan = checkbox('Plan de izado específico (250 €)', 'plan', False)
    cae = checkbox('Gestión documental CAE (60 €)', 'cae', False)
with b:
    res = checkbox('Gestión de residuos (12 €)', 'res', True)
    perm = checkbox('Permisos del ayuntamiento (400 € más tasas)', 'perm', False)
with c:
    rsv = checkbox('Reserva de espacio (600 €)', 'rsv', False)
    pil = number('Vehículos piloto (número)', 'pil', 0)

chosen_ut = []
if g != 'bomba':
    with st.expander('Útiles y accesorios de carga (precio por día)', expanded=False):
        ucols = st.columns(2)
        for i,(name,price) in enumerate(DATA['U'].items()):
            with ucols[i%2]:
                if st.checkbox(f'{name} · {price} €/día', key='ut_'+str(i)):
                    chosen_ut.append((name,price))

# Pricing logic ported from the supplied HTML calculator
if g == 'bomba':
    f = 1 + float(tub)
    add('Desplazamiento de la autobomba', p['dp'])
    if m3 > 55:
        idx = 0 if m3 <= 75 else 1 if m3 <= 100 else 2 if m3 <= 150 else 3 if m3 <= 200 else 4 if m3 <= 300 else 5
        add(f'Bombeo: {m3:g} m³ × {p["t"][idx]:g} €/m³', m3*p['t'][idx]*f, 'Incluye recargo de tubería' if f>1 else 'Tarifa por volumen diario')
    else:
        add(f'Bombeo por horas: {max(hb,3):g} h × {p["h"]:g} €/h', max(hb,3)*p['h']*f, 'Servicio mínimo: desplazamiento + 3 h')
    add('Horas a disposición por bajo rendimiento', hd*p['hd'], f'{p["hd"]:g} €/h')
    add('Horas extra L-V 18-22 h', b18*35, '35 €/h')
    add('Horas nocturnas, sábados y festivos', b22*80, '80 €/h')
    add('Operario especializado en trabajos estáticos', bop*45, '45 €/h')
    add('Servicio con radio superior a 30 km', max(0,km-30)*2*2, '2 €/km, ida y vuelta')
else:
    mo = mode
    days = {'d':n,'w':5*n,'m':20*n,'sc':1}[mo]
    if mo == 'sc':
        sal = p['sm'][0]
        rate = p['d'][2] if 'd' in p else 0
        add(f'Servicio corto: salida + {p["sm"][1]} h incluidas', sal)
        add('Horas adicionales sobre las incluidas', max(0,h0-p['sm'][1])*rate, f'{rate:g} €/h')
    else:
        sal = p[mo][0]
        rate = p[mo][2]
        rental = p[mo][1]
        add('Salida' + ('' if pern else f' × {days:g} días'), sal*(1 if pern else days), 'Incluye hasta 35 km desde Leganés')
        add(f'Alquiler: {n:g} {UNITS[mo]} × {rental:g} €', rental*n)
        if pern and days > 1:
            add(f'Salida del operador ({days-1:g} días desde el 2º)', (days-1)*(p.get('so') or 0), f'{(p.get("so") or 0):g} €/día')
        add('Horas adicionales (8-17 h)', h0*rate, f'{rate:g} €/h')
    f1 = rate*p['pct'] if 'pct' in p else p.get('i1',0)
    f2 = rate*p['pct'] if 'pct' in p else p.get('i2',0)
    hm = p.get('hm',0)
    b2 = max(h2,hm) if h2 else 0
    add('Horas extra L-V 6-8 h y 17-22 h', h1*(rate+f1), f'{rate+f1:g} €/h')
    add('Horas en sábado, domingo, festivo o nocturno', b2*(rate+f2), f'{rate+f2:g} €/h' + (f' · mínimo {hm:g} h' if hm else ''))
    if p.get('pct') and h1+h2>0:
        add('Recargo de horario extraordinario sobre la salida', sal*p['pct'], f'{round(p["pct"]*100)} %')
    extra_km = max(0,km-35)*2
    add('Kilómetros fuera de los 35 km incluidos', extra_km*(p.get('km') or 0), f'{extra_km:g} km ida y vuelta × {(p.get("km") or 0):g} €/km')
    if km > 60: add('Dieta del operador (más de 60 km)', 110*days, '110 €/día')
    if o2 and p.get('o2'): add('Segundo operador auxiliar', p['o2']*8*days, f'{p["o2"]:g} €/h × 8 h/día')
    add('Ayudante de gruista', ah*(42.8 if prov==1 else 53.5))
    add('Dirección técnica', dt*69.55, '69,55 €/h')
    for name,price in chosen_ut: add(name,price*days,f'{price:g} €/día × {days:g}')
if plan: add('Plan de izado específico',250)
if cae: add('Gestión documental CAE',60)
if res: add('Gestión de residuos',12)
if perm: add('Permisos del ayuntamiento (más tasas)',400)
if rsv: add('Reserva de espacio',600)
add('Vehículos piloto',pil*(170+0.6*2*km),'170 € de salida + 0,60 €/km (más 30 €/h según duración)')

subtotal = sum(x[1] for x in L)
vat = subtotal*0.21
total = subtotal+vat

# Two-column quote view
left, right = st.columns([1.8,1], gap='large')
with left:
    st.markdown('<div class="section-title">Detalle del presupuesto</div>', unsafe_allow_html=True)
    st.caption(f'{GROUPS[g][0]} · {selected_label}')
    if L:
        for title, amount, note in L:
            c1,c2 = st.columns([3,1])
            with c1:
                st.markdown(f'**{title}**')
                if note: st.caption(note)
            with c2: st.markdown(f'<div style="text-align:right;font-weight:700;padding-top:4px">{euro(amount)}</div>', unsafe_allow_html=True)
            st.divider()
    else:
        st.info('Configura la máquina y los servicios para ver el presupuesto.')
with right:
    st.markdown(f'<div class="summary-head"><div style="font-size:13px;opacity:.85">PRESUPUESTO ORIENTATIVO</div><div style="font-size:20px;font-weight:750;margin-top:5px">{html.escape(selected_label)}</div></div>', unsafe_allow_html=True)
    st.image(img_bytes(g), use_container_width=True)
    st.metric('Base imponible', euro(subtotal))
    st.metric('IVA (21 %)', euro(vat))
    st.markdown(f'<div class="summary-total"><div style="color:{MUTED};font-size:13px">TOTAL PRESUPUESTO</div><div style="font-size:30px;font-weight:800;color:{GREEN}">{euro(total)}</div></div>', unsafe_allow_html=True)
    st.markdown('<p class="small-muted">Presupuesto orientativo con las tarifas del catálogo Precios Netos 2024. IVA por cuenta del cliente. Se aplican las Condiciones generales de contratación de Transgruma.</p>', unsafe_allow_html=True)

# Printable HTML quote for the user to save/print
rows = ''.join(f'<tr><td>{html.escape(title)}<br><small>{html.escape(note)}</small></td><td style="text-align:right">{euro(amount)}</td></tr>' for title,amount,note in L)
quote_html = f"""<!doctype html><html lang="es"><meta charset="utf-8"><title>Presupuesto orientativo Transgruma</title><style>body{{font-family:Arial,sans-serif;color:#10243a;max-width:900px;margin:35px auto;padding:20px}}header{{background:#0a2342;color:white;padding:20px;border-bottom:5px solid #1b8a4b}}h1{{margin:0}}table{{width:100%;border-collapse:collapse;margin-top:25px}}td,th{{padding:12px;border-bottom:1px solid #ddd;text-align:left}}.total{{text-align:right;font-size:22px;color:#1b8a4b;font-weight:bold}}small{{color:#5b6b7c}}@media print{{button{{display:none}}}}</style><header><h1>Transgruma</h1><p>Elevando su confianza · Precios Netos 2024</p></header><h2>Presupuesto orientativo de alquiler</h2><p><b>Máquina:</b> {html.escape(selected_label)}<br><b>Familia:</b> {html.escape(GROUPS[g][0])}</p><table><thead><tr><th>Concepto</th><th style="text-align:right">Importe</th></tr></thead><tbody>{rows}</tbody></table><p>Base imponible: <b>{euro(subtotal)}</b></p><p>IVA (21 %): <b>{euro(vat)}</b></p><p class="total">TOTAL: {euro(total)}</p><p><small>Presupuesto orientativo con las tarifas del catálogo Precios Netos 2024. IVA por cuenta del cliente. Se aplican las Condiciones generales de contratación de Transgruma.</small></p><button onclick="window.print()">Imprimir / guardar como PDF</button></html>"""
st.download_button('⬇️ Descargar presupuesto imprimible (HTML)', data=quote_html.encode('utf-8'), file_name='presupuesto_transgruma.html', mime='text/html', use_container_width=True)
st.caption('Nota: esta versión reproduce la lógica del HTML facilitado. Antes de usarla comercialmente, conviene contrastar las tarifas y validar los cálculos con Transgruma.')
