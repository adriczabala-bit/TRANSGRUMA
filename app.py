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
    picture = img_bytes(g)
    if picture:
        st.image(picture, use_container_width=True)
    else:
        st.markdown('<div style="height:90px;display:flex;align-items:center;justify-content:center;font-size:44px">🏗️</div>', unsafe_allow_html=True)
    st.metric('Base imponible', euro(subtotal))
    st.metric('IVA (21 %)', euro(vat))
    st.markdown(f'<div class="summary-total"><div style="color:{MUTED};font-size:13px">TOTAL PRESUPUESTO</div><div style="font-size:30px;font-weight:800;color:{GREEN}">{euro(total)}</div></div>', unsafe_allow_html=True)
    st.markdown('<p class="small-muted">Presupuesto orientativo con las tarifas del catálogo Precios Netos 2024. IVA por cuenta del cliente. Se aplican las Condiciones generales de contratación de Transgruma.</p>', unsafe_allow_html=True)

# Printable HTML quote for the user to save/print
rows = ''.join(f'<tr><td>{html.escape(title)}<br><small>{html.escape(note)}</small></td><td style="text-align:right">{euro(amount)}</td></tr>' for title,amount,note in L)
quote_html = f"""<!doctype html><html lang="es"><meta charset="utf-8"><title>Presupuesto orientativo Transgruma</title><style>body{{font-family:Arial,sans-serif;color:#10243a;max-width:900px;margin:35px auto;padding:20px}}header{{background:#0a2342;color:white;padding:20px;border-bottom:5px solid #1b8a4b}}h1{{margin:0}}table{{width:100%;border-collapse:collapse;margin-top:25px}}td,th{{padding:12px;border-bottom:1px solid #ddd;text-align:left}}.total{{text-align:right;font-size:22px;color:#1b8a4b;font-weight:bold}}small{{color:#5b6b7c}}@media print{{button{{display:none}}}}</style><header><h1>Transgruma</h1><p>Elevando su confianza · Precios Netos 2024</p></header><h2>Presupuesto orientativo de alquiler</h2><p><b>Máquina:</b> {html.escape(selected_label)}<br><b>Familia:</b> {html.escape(GROUPS[g][0])}</p><table><thead><tr><th>Concepto</th><th style="text-align:right">Importe</th></tr></thead><tbody>{rows}</tbody></table><p>Base imponible: <b>{euro(subtotal)}</b></p><p>IVA (21 %): <b>{euro(vat)}</b></p><p class="total">TOTAL: {euro(total)}</p><p><small>Presupuesto orientativo con las tarifas del catálogo Precios Netos 2024. IVA por cuenta del cliente. Se aplican las Condiciones generales de contratación de Transgruma.</small></p><button onclick="window.print()">Imprimir / guardar como PDF</button></html>"""
st.download_button('⬇️ Descargar presupuesto imprimible (HTML)', data=quote_html.encode('utf-8'), file_name='presupuesto_transgruma.html', mime='text/html', use_container_width=True)
st.caption('Nota: esta versión reproduce la lógica del HTML facilitado. Antes de usarla comercialmente, conviene contrastar las tarifas y validar los cálculos con Transgruma.')
