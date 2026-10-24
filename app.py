import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Purealign - Portal de Consulta y Cotización",
    page_icon="🦷",
    layout="wide"
)

# --- ESTILOS CSS (TEMA MORADO #6C5BC2 Y VERDE #63CA53) ---
st.markdown("""
    <style>
    /* Fondo general claro y limpio */
    .stApp {
        background-color: #f8f7fc;
    }
    
    /* Títulos e íconos */
    h1, h2, h3 {
        color: #6C5BC2 !important;
        font-weight: 700;
    }
    
    /* Tarjetas de contenedor con borde morado suave */
    .card-box {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border: 2px solid #e3e0f5;
        box-shadow: 0 4px 12px rgba(108, 91, 194, 0.06);
        margin-bottom: 20px;
    }
    
    /* Cajas destacadas de Desglose de Paquete (Fondo Morado Tenue) */
    .desglose-box {
        background-color: #f1effa;
        border-left: 5px solid #6C5BC2;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    /* Resaltados de Precios y Totales (Verde Vibrant #63CA53) */
    .total-destacado {
        color: #63CA53;
        font-size: 26px;
        font-weight: bold;
    }
    
    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dcd7f2;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Botón Principal */
    div.stButton > button:first-child {
        background-color: #6C5BC2;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
    }
    div.stButton > button:first-child:hover {
        background-color: #5849a6;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def conectar_google_sheets():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_credenciales = os.path.join(directorio_actual, "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(ruta_credenciales, SCOPE)
    client = gspread.authorize(creds)
    return client.open("Purealign_DB_Trabajo")

try:
    db = conectar_google_sheets()
    sheet_creditos = db.worksheet("Creditos")
    sheet_adicionales = db.worksheet("Adicionales")
    sheet_pacientes = db.worksheet("Pacientes")

    df_creditos = pd.DataFrame(sheet_creditos.get_all_records())
    df_adicionales = pd.DataFrame(sheet_adicionales.get_all_records())
    df_pacientes = pd.DataFrame(sheet_pacientes.get_all_records())
except Exception as e:
    st.error(f"Error al conectar con Google Sheets. Verifica tu archivo 'credentials.json' y tus pestañas. Detalle: {e}")
    st.stop()

# --- ENCABEZADO ---
st.title("🦷 Purealign - Portal de Consulta y Cotización")
st.markdown("Bienvenido Dr. Héctor Díaz. Consulta transparente de costos, desglose de paquetes y registro de órdenes.")
st.divider()

# ==============================================================================
# SECCIÓN SUPERIOR: REGISTRO DE PACIENTE (IZQ) Y CALCULADORA Y DESGLOSE (DER)
# ==============================================================================
col_sec1, col_sec2 = st.columns([3, 2])

with col_sec1:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("👤 Registro de Paciente y Alineadores")
    
    nombre_paciente = st.text_input("Nombre Completo del Paciente")
    cant_alineadores = st.number_input("Cantidad de Alineadores Requeridos", min_value=1, max_value=60, value=15, step=1)
    
    opciones_paquete = ["Ninguno (Precio Regular $520 c/u)", "Pure Basic (1 a 20 alineadores)", "Pure Extended (21 a 40 alineadores)"]
    paquete_seleccionado = st.selectbox("Seleccionar Paquete / Modalidad", opciones_paquete)

    # --- LÓGICA FINANCIERA Y TEXTOS DE DESGLOSE ---
    costo_individual = cant_alineadores * 520.0
    rango_paquete = ""
    contenido_paquete = ""

    if "Pure Basic" in paquete_seleccionado:
        precio_final = 5120.0
        rango_paquete = "1 a 20 Alineadores"
        contenido_paquete = "✔️ **12 Sets de alineadores extra** (de refinamiento)\n\n✔️ **1 Planeación digital** de tratamiento incluida."
    elif "Pure Extended" in paquete_seleccionado:
        precio_final = 8500.0
        rango_paquete = "21 a 40 Alineadores"
        contenido_paquete = "✔️ **25 Sets de alineadores extra** (de refinamiento)\n\n✔️ **1 Planeación digital** de tratamiento incluida."
    else:
        precio_final = costo_individual
        rango_paquete = f"{cant_alineadores} Alineadores requeridos"
        contenido_paquete = "⚠️ **Esquema de Venta Individual:** No incluye sets de refinamiento extra ni planeaciones incluidas."

    st.markdown('</div>', unsafe_allow_html=True)

with col_sec2:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("📊 Resumen y Desglose de Paquete")
    
    ahorro = max(0.0, costo_individual - precio_final)
    
    st.markdown(f"""
    * **Paciente:** {nombre_paciente if nombre_paciente else '*Pendiente de ingresar*'}
    * **Cantidad Solicitada:** {cant_alineadores} alineadores
    * **Modalidad Seleccionada:** `{paquete_seleccionado}`
    * **Costo Base Sin Descuento:** ${costo_individual:,.2f} MXN
    """)
    
    # CPTA DE DESGLOSE DETALLADO DEL PAQUETE
    st.markdown(f"""
    <div class="desglose-box">
        <h4 style="color: #6C5BC2; margin-top:0;">📦 ¿Qué incluye esta opción?</h4>
        <p><b>Rango de cobertura:</b> {rango_paquete}</p>
        {contenido_paquete}
    </div>
    """, unsafe_allow_html=True)
    
    if ahorro > 0:
        st.markdown(f"<p style='color: #63CA53; font-weight: bold; margin-top: 10px;'>🎉 Ahorro total con convenio: ${ahorro:,.2f} MXN</p>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown(f"**SUBTOTAL PACIENTE:** <span class='total-destacado'>${precio_final:,.2f} MXN</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==============================================================================
# SECCIÓN MEDIA: TOKENS / CRÉDITOS Y PRODUCTOS ADICIONALES
# ==============================================================================
col_mid1, col_mid2 = st.columns([2, 3])

with col_mid1:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("📦 Créditos y Tokens")
    
    if not df_creditos.empty:
        for index, row in df_creditos.iterrows():
            st.metric(label=f"Restantes: {row['Recurso']}", value=f"{row['Restantes']} / {row['Total']}", delta="Disponibles")
    else:
        st.metric(label="Planeaciones", value="3 / 5", delta="Disponibles")
        st.metric(label="Alineadores", value="40 / 100", delta="Disponibles")
        
    if st.button("🛒 Solicitud de Más Créditos", use_container_width=True):
        st.info("Función de consulta. Contacta al laboratorio para adquirir más paquetes de créditos.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid2:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("🛍️ Productos Adicionales y Resumen Final")
    
    total_adicionales = 0.0
    if not df_adicionales.empty:
        for idx, row in df_adicionales.iterrows():
            prod_nombre = row["Producto"]
            prod_precio = float(row["Precio"])
            seleccionado = st.checkbox(f"{prod_nombre} (${prod_precio:,.2f} MXN)", key=f"add_{idx}")
            if seleccionado:
                total_adicionales += prod_precio
    else:
        st.warning("No hay productos adicionales configurados.")
        
    # Total General
    total_general = precio_final + total_adicionales
    
    st.markdown("---")
    st.markdown(f"**Subtotal Adicionales:** ${total_adicionales:,.2f} MXN")
    st.markdown(f"### 💳 Total a Cobrar: <span class='total-destacado'>${total_general:,.2f} MXN</span>", unsafe_allow_html=True)
    
    # Botón principal para guardar en Google Sheets
    if st.button("➕ Registrar Orden en el Historial", type="primary", use_container_width=True):
        if nombre_paciente.strip():
            try:
                sheet_pacientes.append_row([
                    nombre_paciente,
                    cant_alineadores,
                    paquete_seleccionado,
                    f"${costo_individual:,.2f}",
                    f"${total_general:,.2f}"
                ])
                st.success(f"¡Orden para '{nombre_paciente}' registrada correctamente en la base de datos!")
                st.rerun()
            except Exception as e:
                st.error(f"Ocurrió un error al guardar en Google Sheets: {e}")
        else:
            st.warning("⚠️ Por favor ingresa el nombre del paciente antes de registrar la orden.")
            
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==============================================================================
# SECCIÓN INFERIOR: TABLA HISTÓRICA DE PACIENTES
# ==============================================================================
st.markdown('<div class="card-box">', unsafe_allow_html=True)
st.subheader("📋 Historial de Pacientes y Cotizaciones Registradas")
st.markdown("Consulta en tiempo real sincronizada con Google Sheets.")

if not df_pacientes.empty:
    st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
else:
    st.info("No hay órdenes registradas aún en Google Sheets.")
st.markdown('</div>', unsafe_allow_html=True)