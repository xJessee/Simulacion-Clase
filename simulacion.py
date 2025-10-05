import streamlit as st
import numpy as np

# =========================================================================
# FUNCIONES DE PRUEBA (Mantenemos la lógica intacta)
# =========================================================================

def prueba_media(datos, n, Z_critico):
    media_muestral = np.mean(datos)
    Z0 = (media_muestral - 0.5) / np.sqrt(1 / (12 * n))
    apto = abs(Z0) <= Z_critico
    return "✅ Apto" if apto else "❌ No apto"

def prueba_varianza(datos, n, Chi_inf, Chi_sup):
    if n <= 1: return "N/A"
    varianza_muestral = np.var(datos, ddof=1)
    X0_sq = 12 * (n - 1) * varianza_muestral
    apto = (X0_sq >= Chi_inf) and (X0_sq <= Chi_sup)
    st.session_state['X0_sq'] = X0_sq # Guardar para mostrar
    return "✅ Apto" if apto else "❌ No apto"

def prueba_conformidad_ks(datos, n, D_critico):
    datos_ordenados = np.sort(datos)
    i = np.arange(1, n + 1)
    D_plus = np.max((i / n) - datos_ordenados)
    D_minus = np.max(datos_ordenados - ((i - 1) / n))
    D = np.max([D_plus, D_minus])
    apto = D <= D_critico
    st.session_state['D_stat'] = D # Guardar para mostrar
    return "✅ Apto" if apto else "❌ No apto"

def prueba_independencia_corridas(datos, n, Z_critico):
    if n < 3: return "N/A (n < 3)"

    R = 1
    for i in range(2, n):
        if (datos[i] > datos[i-1] and datos[i-1] < datos[i-2]) or \
           (datos[i] < datos[i-1] and datos[i-1] > datos[i-2]):
            R += 1
            
    mu_R = (2 * n - 1) / 3
    sigma2_R = (16 * n - 29) / 90
    Z0 = (R - mu_R) / np.sqrt(sigma2_R)
    
    apto = abs(Z0) <= Z_critico
    st.session_state['Z0_runs'] = Z0 # Guardar para mostrar
    st.session_state['R_count'] = R # Guardar Racha
    return "✅ Apto" if apto else "❌ No apto"

# =========================================================================
# INTERFAZ DE STREAMLIT
# =========================================================================

st.set_page_config(layout="wide")
st.title("🔢 Validador de Números Pseudoaleatorios (Simulación)")
st.markdown("---")

# -----------------
# 1. Entrada de Datos
# -----------------
st.header("1. Ingreso de Datos y Parámetros ($\alpha=0.05$)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Conjunto de Números")
    # Entrada de números separados por coma o espacio
    data_input = st.text_area(
        "Ingrese su secuencia de números (separados por coma, espacio o salto de línea):",
        height=150,
        placeholder="Ej: 0.12, 0.54, 0.98, 0.33, 0.77, 0.45"
    )

with col2:
    st.subheader("Valores Críticos (De sus Tablas)")
    st.warning("Debe obtener estos valores de sus tablas estadísticas para $\\alpha=0.05$ y su $n$")
    
    # Valores Críticos
    Z_critico = st.number_input("$Z_{\\alpha/2}$ (Normal Estándar, ej: 1.96):", value=1.96, format="%.4f")
    D_critico = st.number_input("$D_{\\alpha, n}$ (Kolmogorov-Smirnov):", value=0.1000, format="%.4f")
    Chi_inf = st.number_input("$\\chi^2_{\\alpha/2, n-1}$ (Límite Inferior):", value=0.0000, format="%.4f")
    Chi_sup = st.number_input("$\\chi^2_{1-\\alpha/2, n-1}$ (Límite Superior):", value=20.0000, format="%.4f")

st.markdown("---")

# -----------------
# 2. Procesamiento
# -----------------

if st.button("▶️ Ejecutar Pruebas de Aleatoriedad"):
    try:
        # Limpieza y conversión de datos a float
        datos_str = [x.strip() for x in data_input.replace(',', ' ').split()]
        datos = np.array([float(x) for x in datos_str if x])
        n = len(datos)

        if n < 2:
            st.error("Debe ingresar al menos 2 números para realizar las pruebas.")
        else:
            # Ejecución de las pruebas
            st.session_state['media'] = prueba_media(datos, n, Z_critico)
            st.session_state['varianza'] = prueba_varianza(datos, n, Chi_inf, Chi_sup)
            st.session_state['ks'] = prueba_conformidad_ks(datos, n, D_critico)
            st.session_state['corridas'] = prueba_independencia_corridas(datos, n, Z_critico)
            st.session_state['n'] = n
            st.session_state['datos'] = datos.tolist()
            st.session_state['run_result'] = True
            
    except ValueError:
        st.error("Error al procesar los datos. Asegúrese de ingresar solo números válidos entre 0 y 1.")

# -----------------
# 3. Resultados
# -----------------

if 'run_result' in st.session_state and st.session_state['run_result']:
    st.header(f"2. Resultados de las Pruebas ($n={st.session_state['n']}$)")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.subheader("Resumen de Aprobación")
        st.info("Un conjunto de números pseudoaleatorios ideal debe ser **Apto** en todas las pruebas.")
        
        # Tabla de resultados simple
        st.markdown(
            f"""
            | Prueba | Resultado |
            | :--- | :--- |
            | **Media** | {st.session_state['media']} |
            | **Varianza** | {st.session_state['varianza']} |
            | **Conformidad (K-S)** | {st.session_state['ks']} |
            | **Independencia (Corridas)** | {st.session_state['corridas']} |
            """
        )

    with col_res2:
        st.subheader("Estadísticos Calculados")
        # Mostrar los estadísticos calculados para revisión
        st.markdown(
            f"""
            - **Media muestral ($\\bar{R}$):** {np.mean(st.session_state['datos']):.5f}
            - **Estadístico $\\chi^2_0$ (Varianza):** {st.session_state.get('X0_sq', 'N/A'):.4f}
            - **Estadístico $D$ (K-S):** {st.session_state.get('D_stat', 'N/A'):.4f}
            - **Estadístico $Z_0$ (Corridas):** {st.session_state.get('Z0_runs', 'N/A'):.4f} (Rachas: {st.session_state.get('R_count', 'N/A')})
            """
        )