import streamlit as st
import requests
import json
import random
from datetime import datetime
import time

# Configuración de la página
st.set_page_config(
    page_title="Generador de CC",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado y compatible
st.markdown("""
<style>
    /* Reset y configuración base */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Título principal */
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 1rem 0 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Contenedores personalizados */
    .custom-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
    }
    
    /* Área de resultados */
    .results-area {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.4;
        min-height: 200px;
        white-space: pre-wrap;
        overflow-x: auto;
        color: #2c3e50;
    }
    
    /* Métricas personalizadas */
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        min-width: 120px;
        margin: 0.5rem;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        display: block;
    }
    
    .metric-label {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-top: 0.2rem;
    }
    
    /* Estados de mensajes */
    .success-msg {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    .error-msg {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    .info-msg {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .metric-container {
            flex-direction: column;
            align-items: center;
        }
        .metric-box {
            width: 90%;
            margin: 0.3rem 0;
        }
        .custom-container {
            padding: 1rem;
        }
    }
    
    /* Botones personalizados */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar personalizado */
    .css-1d391kg {
        background: #2c3e50;
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

def generar_luhn(bin_prefix):
    """Genera un número de tarjeta válido usando el algoritmo de Luhn"""
    numero_sin_verificar = ''
    for digito in bin_prefix:
        if digito.lower() == 'x':
            numero_sin_verificar += str(random.randint(0, 9))
        else:
            numero_sin_verificar += digito
    
    if not numero_sin_verificar.isdigit():
        raise ValueError("El BIN debe contener solo dígitos o 'x'")
    
    if len(numero_sin_verificar) > 15:
        numero_sin_verificar = numero_sin_verificar[:15]
    elif len(numero_sin_verificar) < 15:
        numero_sin_verificar = numero_sin_verificar + '0' * (15 - len(numero_sin_verificar))
    
    suma = 0
    for i, digito in enumerate(reversed(numero_sin_verificar)):
        n = int(digito)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    
    digito_verificacion = (10 - (suma % 10)) % 10
    return numero_sin_verificar + str(digito_verificacion)

def verificar_luhn(numero):
    """Verifica si un número de tarjeta cumple con el algoritmo de Luhn"""
    if not numero.isdigit():
        return False
        
    suma = 0
    for i, digito in enumerate(reversed(numero)):
        n = int(digito)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
            
    return suma % 10 == 0

def obtener_info_bin(bin_number):
    """Obtiene información del BIN usando la API de binlist.net"""
    try:
        headers = {'Accept-Version': '3'}
        response = requests.get(f'https://lookup.binlist.net/{bin_number}', headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

# Inicializar session state
if 'tarjetas_guardadas' not in st.session_state:
    st.session_state.tarjetas_guardadas = []

if 'resultados_actuales' not in st.session_state:
    st.session_state.resultados_actuales = []

# Título principal
st.markdown('<h1 class="main-title">💳 Generador de CC Friends School</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Generador profesional de números de tarjeta con validación Luhn</p>', unsafe_allow_html=True)

# Sidebar para controles
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    # Campo BIN
    bin_input = st.text_input(
        "BIN (usa 'x' para dígitos aleatorios):",
        value="453900xxxxxxxxxx",
        help="Ingresa el BIN base. Usa 'x' para generar dígitos aleatorios",
        key="bin_input"
    )
    
    st.markdown("### 📅 Fecha de Expiración")
    
    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mes", [f"{i:02d}" for i in range(1, 13)], key="mes_select")
    with col2:
        año = st.selectbox("Año", [f"{i:02d}" for i in range(24, 31)], index=0, key="año_select")
    
    if st.button("🎲 Fecha Aleatoria", key="fecha_aleatoria"):
        st.session_state.mes_random = f"{random.randint(1, 12):02d}"
        st.session_state.año_random = f"{random.randint(24, 30):02d}"
        st.rerun()
    
    # Aplicar fecha aleatoria si existe
    if 'mes_random' in st.session_state:
        mes = st.session_state.mes_random
        del st.session_state.mes_random
    if 'año_random' in st.session_state:
        año = st.session_state.año_random
        del st.session_state.año_random
    
    # Cantidad
    cantidad = st.selectbox(
        "Cantidad de tarjetas:",
        [10, 15, 25, 50],
        key="cantidad_select"
    )
    
    st.markdown("---")
    st.markdown("### 🔗 Enlaces Útiles")
    if st.button("📧 Correo Temporal", key="correo_temp"):
        st.markdown("[🔗 Abrir Temp-Mail](https://temp-mail.org/es/)")

# Contenido principal con pestañas
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generador", "🔍 BIN Checker", "💾 Guardadas", "ℹ️ Información"])

with tab1:
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 GENERAR TARJETAS", type="primary", key="generar_btn"):
            if not bin_input.strip():
                st.markdown('<div class="error-msg">❌ Por favor ingrese un BIN válido</div>', unsafe_allow_html=True)
            else:
                # Procesar BIN
                bin_base = bin_input.strip().replace(' ', '')
                if len(bin_base) < 16:
                    bin_base = bin_base + 'x' * (16 - len(bin_base))
                bin_base = bin_base[:15]  # Solo necesitamos 15 dígitos para el algoritmo
                
                # Contenedor de progreso
                progress_container = st.empty()
                results_container = st.empty()
                
                # Generar tarjetas
                resultados = []
                tarjetas_generadas = 0
                intentos = 0
                max_intentos = cantidad * 20
                
                progress_container.markdown("⏳ Generando tarjetas válidas...")
                progress_bar = st.progress(0)
                
                start_time = time.time()
                
                while tarjetas_generadas < cantidad and intentos < max_intentos:
                    intentos += 1
                    try:
                        tarjeta = generar_luhn(bin_base)
                        if verificar_luhn(tarjeta):
                            cvv = str(random.randint(100, 999))
                            resultado = f"{tarjeta}|{mes}|{año}|{cvv}"
                            resultados.append(resultado)
                            tarjetas_generadas += 1
                            progress_bar.progress(tarjetas_generadas / cantidad)
                    except:
                        continue
                
                progress_bar.empty()
                progress_container.empty()
                
                # Mostrar resultados
                if resultados:
                    st.session_state.resultados_actuales = resultados
                    generation_time = round(time.time() - start_time, 2)
                    success_rate = round((len(resultados) / intentos) * 100, 1)
                    
                    st.markdown('<div class="success-msg">✅ Tarjetas generadas exitosamente!</div>', unsafe_allow_html=True)
                    
                    # Métricas
                    st.markdown(f'''
                    <div class="metric-container">
                        <div class="metric-box">
                            <span class="metric-value">{len(resultados)}</span>
                            <div class="metric-label">Tarjetas Generadas</div>
                        </div>
                        <div class="metric-box">
                            <span class="metric-value">{intentos}</span>
                            <div class="metric-label">Intentos Totales</div>
                        </div>
                        <div class="metric-box">
                            <span class="metric-value">{success_rate}%</span>
                            <div class="metric-label">Tasa de Éxito</div>
                        </div>
                        <div class="metric-box">
                            <span class="metric-value">{generation_time}s</span>
                            <div class="metric-label">Tiempo Generación</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Mostrar tarjetas
                    resultado_texto = "\n".join(resultados)
                    st.markdown("### 📋 Tarjetas Generadas:")
                    st.markdown(f'<div class="results-area">{resultado_texto}</div>', unsafe_allow_html=True)
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("💾 Guardar", key="guardar_btn"):
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            for tarjeta in resultados:
                                st.session_state.tarjetas_guardadas.append({
                                    'tarjeta': tarjeta,
                                    'fecha': timestamp
                                })
                            st.markdown('<div class="success-msg">💾 Tarjetas guardadas exitosamente</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.download_button(
                            label="⬇️ Descargar",
                            data=resultado_texto,
                            file_name=f"tarjetas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            key="download_btn"
                        )
                    
                    with col3:
                        if st.button("🔄 Generar Más", key="mas_btn"):
                            st.rerun()
                
                else:
                    st.markdown('<div class="error-msg">❌ No se pudieron generar tarjetas válidas</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Verificador de BIN")
    
    bin_check = st.text_input(
        "Ingresa el BIN a verificar (mínimo 6 dígitos):",
        value=bin_input[:8] if bin_input else "",
        key="bin_check_input"
    )
    
    if st.button("🔎 VERIFICAR BIN", key="verificar_btn"):
        if len(bin_check.replace('x', '').replace('X', '')) >= 6:
            # Limpiar el BIN
            bin_clean = bin_check.replace('x', '').replace('X', '')[:8]
            
            with st.spinner("🔍 Consultando información del BIN..."):
                data = obtener_info_bin(bin_clean)
                
                if data:
                    st.markdown('<div class="success-msg">✅ Información del BIN encontrada</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💳 Información de la Tarjeta")
                        st.markdown(f"**Esquema:** {data.get('scheme', 'N/A').upper()}")
                        st.markdown(f"**Tipo:** {data.get('type', 'N/A').title()}")
                        st.markdown(f"**Marca:** {data.get('brand', 'N/A').upper()}")
                        
                        if 'prepaid' in data:
                            prepaid_status = "Sí" if data['prepaid'] else "No"
                            st.markdown(f"**Prepagada:** {prepaid_status}")
                    
                    with col2:
                        if 'country' in data:
                            st.markdown("#### 🌍 Información del País")
                            country = data['country']
                            st.markdown(f"**País:** {country.get('name', 'N/A')} {country.get('emoji', '')}")
                            st.markdown(f"**Código:** {country.get('alpha2', 'N/A')}")
                            st.markdown(f"**Moneda:** {country.get('currency', 'N/A')}")
                    
                    if 'bank' in data and data['bank']:
                        st.markdown("#### 🏦 Información del Banco")
                        bank = data['bank']
                        if bank.get('name'):
                            st.markdown(f"**Banco:** {bank['name']}")
                        if bank.get('url'):
                            st.markdown(f"**Sitio Web:** {bank['url']}")
                        if bank.get('phone'):
                            st.markdown(f"**Teléfono:** {bank['phone']}")
                        if bank.get('city'):
                            st.markdown(f"**Ciudad:** {bank['city']}")
                else:
                    st.markdown('<div class="error-msg">❌ No se pudo obtener información del BIN. Verifica que el BIN sea válido.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-msg">⚠️ Por favor ingrese un BIN válido (mínimo 6 dígitos numéricos)</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="custom-container" >', unsafe_allow_html=True)
    st.markdown("### 💾 Tarjetas Guardadas")
    
    if st.session_state.tarjetas_guardadas:
        st.markdown(f'<div class="info-msg">📊 Total de tarjetas guardadas: {len(st.session_state.tarjetas_guardadas)}</div>', unsafe_allow_html=True)
        
        # Mostrar últimas 10 tarjetas
        for i, item in enumerate(st.session_state.tarjetas_guardadas[-10:], 1):
            with st.expander(f"💳 Tarjeta {i} - {item['fecha']}", expanded=False):
                st.code(item['tarjeta'], language=None)
        
        if len(st.session_state.tarjetas_guardadas) > 10:
            st.markdown('<div class="info-msg ">ℹ️ Mostrando las últimas 10 tarjetas. Descarga el archivo para ver todas.</div>', unsafe_allow_html=True)
        
        # Opciones de gestión
        col1, col2 = st.columns(2)
        with col1:
            todas_las_tarjetas = "\n".join([item['tarjeta'] for item in st.session_state.tarjetas_guardadas])
            st.download_button(
                label="⬇️ Descargar Todas",
                data=todas_las_tarjetas,
                file_name=f"todas_las_tarjetas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_all_btn"
            )
        
        with col2:
            if st.button("🗑️ Limpiar Todas", key="clear_btn"):
                st.session_state.tarjetas_guardadas = []
                st.markdown('<div class="success-msg">🗑️ Todas las tarjetas han sido eliminadas</div>', unsafe_allow_html=True)
                st.rerun()
    else:
        st.markdown('<div class="info-msg">📝 No hay tarjetas guardadas todavía. Genera algunas tarjetas y guárdalas desde la pestaña Generador.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ℹ️ Información de la Aplicación")
        st.markdown('''
        **Generador de BIN CC - Versión Streamlit**
        
        Esta aplicación genera números de tarjeta de crédito válidos usando el algoritmo de Luhn para propósitos educativos y de testing.
        
        **🔧 Características principales:**
        - ✅ Validación con algoritmo de Luhn
        - 🔍 Verificador de BIN integrado con API
        - 💾 Sistema de guardado de tarjetas
        - 📱 Interfaz web responsive
        - 🎲 Generación aleatoria automática
        - ⬇️ Descarga de archivos TXT
        
        **⚠️ Aviso Legal:**
        Esta herramienta es solo para fines educativos y de testing. No debe usarse para actividades fraudulentas.
        ''')
    
    with col2:
        st.markdown("### 👥 Créditos y Información")
        st.markdown('''
        **Desarrollado por:**
        - 🎓 Curso Python Friends School
        - 🔧 Versión: Streamlit Pro v2.0
        
        **🛠️ Tecnologías utilizadas:**
        - Python 3.x
        - Streamlit Framework
        - Requests Library
        - BinList.net API
        
        **📋 Formato de salida:**
        ```
        NUMERO_TARJETA|MES|AÑO|CVV
        ```
        
        **🔗 Enlaces de interés:**
        - [BIN Database](https://binlist.net/)
        - [Luhn Algorithm](https://en.wikipedia.org/wiki/Luhn_algorithm)
        ''')
    
    # Estadísticas de uso (si hay datos)
    if st.session_state.tarjetas_guardadas:
        st.markdown("### 📊 Estadísticas de Uso")
        total_guardadas = len(st.session_state.tarjetas_guardadas)
        st.markdown(f"- **Total de tarjetas guardadas:** {total_guardadas}")
        
        # Análisis de BINs más usados
        bins_usados = {}
        for item in st.session_state.tarjetas_guardadas:
            bin_prefix = item['tarjeta'][:6]
            bins_usados[bin_prefix] = bins_usados.get(bin_prefix, 0) + 1
        
        if bins_usados:
            bin_mas_usado = max(bins_usados, key=bins_usados.get)
            st.markdown(f"- **BIN más generado:** {bin_mas_usado} ({bins_usados[bin_mas_usado]} veces)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #7f8c8d; padding: 1rem;">💳 Generador de CC - Friends School © 2024 | Versión Streamlit</div>',
    unsafe_allow_html=True
)