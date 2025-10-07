import streamlit as st
import numpy as np
from scipy.stats import norm, chi2

# =========================================================================
# FUNCIONES DE PRUEBA
# =========================================================================

def prueba_media(datos, n, Z_critico):
    media_muestral = np.mean(datos)
    Z0 = (media_muestral - 0.5) / np.sqrt(1 / (12 * n))
    apto = abs(Z0) <= Z_critico
    st.session_state['Z0_media'] = Z0
    return "✅ Apto" if apto else "❌ No apto"

def prueba_varianza(datos, n, Chi_inf, Chi_sup):
    if n <= 1: return "N/A"
    varianza_muestral = np.var(datos, ddof=1)
    X0_sq = 12 * (n - 1) * varianza_muestral
    apto = (X0_sq >= Chi_inf) and (X0_sq <= Chi_sup)
    st.session_state['X0_sq'] = X0_sq
    return "✅ Apto" if apto else "❌ No apto"

def prueba_conformidad_ks(datos, n, D_critico):
    datos_ordenados = np.sort(datos)
    i = np.arange(1, n + 1)
    D_plus = np.max((i / n) - datos_ordenados)
    D_minus = np.max(datos_ordenados - ((i - 1) / n))
    D = np.max([D_plus, D_minus])
    apto = D <= D_critico
    st.session_state['D_stat'] = D
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
    st.session_state['Z0_runs'] = Z0
    st.session_state['R_count'] = R
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
st.header("1. Parámetros de Entrada")

col1, col2 = st.columns(2)

with col1:
    n = st.number_input("Tamaño de la muestra (n):", min_value=2, value=5, step=1)
    alpha = st.number_input("Nivel de significancia (α):", min_value=0.001, max_value=0.20, value=0.05, step=0.01, format="%.3f")

with col2:
    st.subheader("Opciones de ingreso de datos")
    data_input = st.text_area(
        "Ingrese su secuencia de números (opcional):",
        height=150,
        placeholder="Ej: 0.12, 0.54, 0.98, 0.33, 0.77"
    )
    generar_auto = st.checkbox("🔄 Generar automáticamente los números aleatorios", value=True)

st.markdown("---")

# -----------------
# 2. Ejecución de Pruebas
# -----------------
if st.button("▶️ Ejecutar Pruebas de Aleatoriedad"):
    try:
        # Si el usuario elige generar los números automáticamente
        if generar_auto or not data_input.strip():
            datos = np.round(np.random.rand(n), 2)
        else:
            datos_str = [x.strip() for x in data_input.replace(',', ' ').split()]
            datos = np.array([float(x) for x in datos_str if x])
            n = len(datos)

        # Validaciones
        if len(datos) < 2:
            st.error("Debe ingresar al menos 2 números para realizar las pruebas.")
            st.stop()
        if np.any((datos < 0) | (datos > 1)):
            st.error("Todos los números deben estar entre 0 y 1.")
            st.stop()

        # ----------------------------
        # Cálculo de valores críticos
        # ----------------------------
        Z_critico = norm.ppf(1 - alpha/2)
        D_critico = 1.36 / np.sqrt(n)
        Chi_inf = chi2.ppf(alpha/2, df=n-1)
        Chi_sup = chi2.ppf(1 - alpha/2, df=n-1)

        # ----------------------------
        # Ejecución de las pruebas
        # ----------------------------
        st.session_state['media'] = prueba_media(datos, n, Z_critico)
        st.session_state['varianza'] = prueba_varianza(datos, n, Chi_inf, Chi_sup)
        st.session_state['ks'] = prueba_conformidad_ks(datos, n, D_critico)
        st.session_state['corridas'] = prueba_independencia_corridas(datos, n, Z_critico)
        st.session_state['datos'] = datos.tolist()
        st.session_state['n'] = n
        st.session_state['alpha'] = alpha
        st.session_state['Zcrit'] = Z_critico
        st.session_state['Dcrit'] = D_critico
        st.session_state['Chi_inf'] = Chi_inf
        st.session_state['Chi_sup'] = Chi_sup
        st.session_state['run_result'] = True

    except ValueError:
        st.error("Error al procesar los datos. Asegúrese de ingresar solo números válidos entre 0 y 1.")

# -----------------
# 3. Resultados
# -----------------
if 'run_result' in st.session_state and st.session_state['run_result']:
    st.header(f"2. Resultados de las Pruebas (n={st.session_state['n']}, α={st.session_state['alpha']})")

    col_res1, col_res2, col_res3 = st.columns(3)

    # Tabla de resultados
    with col_res1:
        st.subheader("🧮 Resultados de Pruebas")
        st.markdown(
            f"""
            | Prueba | Resultado |
            | :--- | :--- |
            | **Media** | {st.session_state['media']} |
            | **Varianza** | {st.session_state['varianza']} |
            | **Uniformidad (K-S)** | {st.session_state['ks']} |
            | **Independencia (Corridas)** | {st.session_state['corridas']} |
            """
        )

    # Tabla de valores críticos
    with col_res2:
        st.subheader("📊 Valores Críticos Calculados")
        st.markdown(
            f"""
            - **Zₐ/₂:** {st.session_state['Zcrit']:.4f}  
            - **Dₐ,n:** {st.session_state['Dcrit']:.4f}  
            - **χ² (Límite Inferior):** {st.session_state['Chi_inf']:.4f}  
            - **χ² (Límite Superior):** {st.session_state['Chi_sup']:.4f}  
            """
        )

    # Estadísticos calculados
    with col_res3:
        st.subheader("📈 Estadísticos Calculados")
        st.markdown(
            f"""
            - **Media muestral (R̄):** {np.mean(st.session_state['datos']):.4f}  
            - **χ²₀ (Varianza):** {st.session_state.get('X0_sq', 'N/A'):.4f}  
            - **D (K-S):** {st.session_state.get('D_stat', 'N/A'):.4f}  
            - **Z₀ (Corridas):** {st.session_state.get('Z0_runs', 'N/A'):.4f} (Rachas: {st.session_state.get('R_count', 'N/A')})
            """
        )

    st.markdown("---")
    st.subheader("🎲 Secuencia Analizada")
    st.write(st.session_state['datos'])
