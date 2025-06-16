import pandas as pd          # Manejo y análisis de datos en estructuras tipo tabla (DataFrames)
import matplotlib.pyplot as plt  # Creación de gráficos estáticos (barras, pasteles, boxplots, etc.)
import seaborn as sns        # Visualización estadística avanzada y gráfica más estética sobre matplotlib
import numpy as np           # Cálculos numéricos y operaciones con arreglos, estadística básica
import streamlit as st       # Framework para crear aplicaciones web interactivas fácilmente
from scipy import stats      # Funciones estadísticas avanzadas como moda, pruebas, etc.
from fpdf import FPDF        # Generar documentos PDF desde Python, agregar texto e imágenes
import tempfile              # Crear archivos temporales para guardar imágenes o datos temporales
import os                    # Manejo de sistema de archivos (eliminar archivos temporales, rutas, etc.)
import re                    # Expresiones regulares para manipular y limpiar texto (ej. quitar emojis)
from PIL import Image        # Biblioteca Pillow para abrir y manejar imágenes (dimensiones, formatos)

# Cargar archivo Excel
df = pd.read_excel("Calificaciones 1 y 2 parcial Plantel Xonacatlán.xlsx")

# Configurar Streamlit
st.set_page_config(layout="wide", page_title="Análisis de Calificaciones")
st.title("📊 Análisis de Calificaciones por Asignatura")

# Filtro de semestre
semestres = df["Semestre"].dropna().unique()
semestre_seleccionado = st.sidebar.selectbox("Selecciona un semestre", sorted(semestres))

# Filtro de carrera dinámico según semestre
carreras_filtradas = df[df["Semestre"] == semestre_seleccionado]["Carrera"].dropna().unique()
carrera_seleccionada = st.sidebar.selectbox("Selecciona una carrera", sorted(carreras_filtradas))

# Filtro de grupo dinámico según semestre y carrera
grupos_filtrados = df[
    (df["Semestre"] == semestre_seleccionado) &
    (df["Carrera"] == carrera_seleccionada)
]["Grupo"].dropna().unique()
grupo_seleccionado = st.sidebar.selectbox("Selecciona un grupo", sorted(grupos_filtrados))

# Filtrar el DataFrame base según todos los filtros
df_filtrado = df[
    (df["Semestre"] == semestre_seleccionado) &
    (df["Carrera"] == carrera_seleccionada) &
    (df["Grupo"] == grupo_seleccionado)
]

# Filtro de asignatura
todas_asignaturas = df_filtrado["Asignatura"].dropna().unique()
asignatura_seleccionada = st.sidebar.selectbox("Selecciona una asignatura", sorted(todas_asignaturas))

# Filtrado final
grupo_df = df_filtrado[df_filtrado["Asignatura"] == asignatura_seleccionada]

# Encabezado personalizado con estilo moderno
st.markdown(f"""
<style>
.encabezado-box {{
    background: linear-gradient(90deg, #1f1f1f, #2c2c2c);
    border-left: 5px solid #00ffd5;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 25px;
}}
.encabezado-box h4 {{
    color: #00ffd5;
    margin: 0;
    font-size: 20px;
}}

</style>

<div class="encabezado-box">
    <h4>🎓 Carrera: <span style='color:white'>{carrera_seleccionada}</span></h4>
    <h4>📘 Asignatura: <span style='color:white'>{asignatura_seleccionada}</span></h4>
    <h4>👥 Grupo: <span style='color:white'>{grupo_seleccionado}</span> | 🗓️ Semestre: <span style='color:white'>{semestre_seleccionado}</span></h4>
</div>
""", unsafe_allow_html=True)

# Colores para rangos
rango_colores = {
    '5-6': '#ff073a',  # rojo neón
    '6-7': '#ff9f1c',  # naranja neón
    '7-8': '#ffe066',  # amarillo neón
    '8-9': '#3cee54',  # verde neón
    '9-10': '#00FF00'  # verde brillante neón
}
rango_bins = [5, 6, 7, 8, 9, 10.1]
rango_labels = ['5-6', '6-7', '7-8', '8-9', '9-10']

calificaciones_dict = {}
estadisticas_dict = {}

cols = st.columns(2)  # Dividimos en 2 columnas horizontales

for idx, parcial in enumerate(['P1', 'P2']):
    calificaciones = grupo_df[parcial].dropna()
    calificaciones_dict[parcial] = calificaciones
    

    if calificaciones.empty:
        cols[idx].warning(f"⚠️ Estadísticas de {parcial}: No disponibles")
        continue   

    # Cálculos principales
    media = calificaciones.mean()
    mediana = calificaciones.median()
    moda = stats.mode(calificaciones, nan_policy='omit', keepdims=True)[0][0]
    varianza = calificaciones.var()
    q1 = calificaciones.quantile(0.25)
    q2 = calificaciones.quantile(0.50)
    q3 = calificaciones.quantile(0.75)

    # Cálculos adicionales por que yo lo digo jaja xd 
    maximo = calificaciones.max()
    minimo = calificaciones.min()
    rango = maximo - minimo
    total = calificaciones.count()

     # ✅ Luego de lso calculos los guardamos en el diccionario
    estadisticas_dict[parcial] = {
        "media": media,
        "mediana": mediana,
        "moda": moda,
        "varianza": varianza,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "max": maximo,
        "min": minimo,
        "rango": rango,
        "total": total
    }
    # HTML con estilos para las tablas
    tabla_html = f"""
    <style>
        .tabla-estadisticas {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 10px;
        }}
        .tabla-estadisticas th, .tabla-estadisticas td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        .tabla-estadisticas th {{
            background-color: #1f1f1f;
            color: #00ffd5;
        }}
        .tabla-estadisticas td {{
            color: #ffffff;
            background-color: #121212;
        }}
        .tabla-estadisticas tr:hover td {{
            background-color: #222;
        }}
    </style>

    <h4 style='color:#00ffd5;'>🔹 Estadísticas de {parcial}</h4>
    <table class="tabla-estadisticas">
        <thead>
            <tr>
                <th>📌 Medida</th>
                <th>🔢 Valor</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Total de Alumnos</td><td>{total}</td></tr>
            <tr><td>Media</td><td>{media:.2f}</td></tr>
            <tr><td>Mediana</td><td>{mediana:.2f}</td></tr>
            <tr><td>Moda</td><td>{moda:.2f}</td></tr>
            <tr><td>Varianza</td><td>{varianza:.2f}</td></tr>
            <tr><td>Rango</td><td>{rango:.2f}</td></tr>
            <tr><td>Q1 (25%)</td><td>{q1:.2f}</td></tr>
            <tr><td>Q2 (50%)</td><td>{q2:.2f}</td></tr>
            <tr><td>Q3 (75%)</td><td>{q3:.2f}</td></tr>
        </tbody>
    </table>
    """

    # Mostrar la tabla en su columna correspondiente
    cols[idx].markdown(tabla_html, unsafe_allow_html=True)

# --- CONTENEDOR VISUAL DEL BOT ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background-color:#1e1e1e; padding:15px; border-radius:12px; border-left:5px solid #00ffd5; margin-bottom:10px;'>
    <h3 style='color:#00ffd5;'>🤖 EduBot</h3>
    <p style='color:white; font-size:14px;'>¡Hola! Soy EduBot, tu asistente de estadísticas. Hazme preguntas como:</p>
    <ul style='color:white; font-size:13px;'>
        <li>¿Qué es la media?</li>
        <li>¿Qué significa boxplot?</li>
        <li>¿Para qué sirve la varianza?</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Activar el bot
bot_activado = st.sidebar.checkbox("💬 Mostrar Bot de Ayuda")

if bot_activado:
    st.sidebar.markdown("### ✏️ Escribe tu duda o elige una sugerencia:")

    # --- Pregunta rápida por botones ---
    pregunta = ""
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📊 Media"):
            pregunta = "media"
        elif st.button("📈 Mediana"):
            pregunta = "mediana"
        elif st.button("📦 Boxplot"):
            pregunta = "boxplot"
    with col2:
        if st.button("📌 Moda"):
            pregunta = "moda"
        elif st.button("📉 Varianza"):
            pregunta = "varianza"

    # Campo para escribir texto libre
    if pregunta == "":
        pregunta = st.sidebar.text_input("O escribe tu pregunta:", key="input_pregunta")

    # --- RESPUESTAS DETALLADAS DEL BOT ---
    if pregunta:
        pregunta = pregunta.lower()

        with st.sidebar:
            with st.spinner("Pensando en una respuesta... 🤔"):
                import time
                time.sleep(1)  # Simulación realista

        if "media" in pregunta:
            p1 = estadisticas_dict['P1']['media']
            p2 = estadisticas_dict['P2']['media']
            
            st.sidebar.markdown("📊 **Media**")
            st.sidebar.info("La media es el promedio de todas las calificaciones. Nos ayuda a identificar el rendimiento general.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")
            
            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** La media subió, los valores más frecuentes fueron más altos en P2.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** La media bajó, los valores más repetidos fueron más bajos en P2.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** La media se mantuvo igual en ambos parciales.")

        elif "moda" in pregunta:
            p1 = estadisticas_dict['P1']['moda']
            p2 = estadisticas_dict['P2']['moda']
            
            st.sidebar.markdown("📌 **Moda**")
            st.sidebar.info("La moda es el valor que más se repite. Si cambia entre parciales, indica un cambio en las calificaciones más comunes.")
            st.sidebar.success(f"🟢 **P1:** {p1:.2f}  \n🔵 **P2:** {p2:.2f}")
            
            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** La moda subió, los valores más frecuentes fueron más altos en P2.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** La moda bajó, los valores más repetidos fueron más bajos en P2.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** La moda se mantuvo igual en ambos parciales.")

        elif "mediana" in pregunta:
            p1 = estadisticas_dict['P1']['mediana']
            p2 = estadisticas_dict['P2']['mediana']
            
            st.sidebar.markdown("📈 **Mediana**")
            st.sidebar.info("Divide los datos ordenados por la mitad. Menos sensible a extremos que la media.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")
            
            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** La mediana subió, los valores más frecuentes fueron más altos en P2.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** La mediana bajó, los valores más repetidos fueron más bajos en P2.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** La mediana se mantuvo igual en ambos parciales.")

        elif "varianza" in pregunta:
            p1 = estadisticas_dict['P1']['varianza']
            p2 = estadisticas_dict['P2']['varianza']
            
            st.sidebar.markdown("📉 **Varianza**")
            st.sidebar.info("Mide qué tanto se alejan los datos de la media. Alta varianza = calificaciones más dispersas.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")
            
            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** La varianza aumentó en P2, lo que indica mayor variación entre las calificaciones del grupo.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** La varianza disminuyó, lo que sugiere que las calificaciones estuvieron más agrupadas en P2.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** La varianza se mantuvo igual, no hubo cambio en la dispersión del rendimiento entre parciales.")

        elif "rango" in pregunta:
            p1 = estadisticas_dict['P1']['rango']
            p2 = estadisticas_dict['P2']['rango']

            st.sidebar.markdown("📏 **Rango (Máx - Mín)**")
            st.sidebar.info("El rango muestra qué tan dispersas están las calificaciones, comparando la más alta con la más baja.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")

            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** Aumentó el rango en P2, lo que indica mayor variabilidad entre los alumnos.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** Disminuyó el rango en P2, lo que sugiere que las calificaciones fueron más homogéneas.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** El rango se mantuvo igual, la dispersión fue la misma en ambos parciales.")

        elif "q1" in pregunta or "cuartil 1" in pregunta:
            p1 = estadisticas_dict['P1']['q1']
            p2 = estadisticas_dict['P2']['q1']

            st.sidebar.markdown("🟪 **Q1 (Primer Cuartil - 25%)**")
            st.sidebar.info("Indica que el 25% de las calificaciones están por debajo de este valor. Es útil para ver cómo está el rendimiento más bajo.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")

            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** El Q1 subió en P2, los alumnos con menor rendimiento mejoraron.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** El Q1 bajó, indicando un desempeño más bajo en el 25% inferior.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** No hubo cambio en el Q1, el rendimiento inferior se mantuvo igual.")

        elif "q2" in pregunta or "cuartil 2" in pregunta:
            p1 = estadisticas_dict['P1']['q2']
            p2 = estadisticas_dict['P2']['q2']
            
            st.sidebar.markdown("🔵 **Q2 (Mediana 50%)**")
            st.sidebar.info("Mitad de alumnos sacó menos y mitad más que este valor.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")
            
            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** El Q2 subió en P2, los alumnos con menor rendimiento mejoraron.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** El Q2 bajó, indicando un desempeño más bajo en el 50% inferior.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** No hubo cambio en el Q2, el rendimiento inferior se mantuvo igual.")

        elif "q3" in pregunta or "cuartil 3" in pregunta:
            p1 = estadisticas_dict['P1']['q3']
            p2 = estadisticas_dict['P2']['q3']
            
            st.sidebar.markdown("🟥 **Q3 (75%)**")
            st.sidebar.info("El 75% de los alumnos sacó menos o igual que este valor.")
            st.sidebar.success(f"🟢 P1: {p1:.2f}  \n🔵 P2: {p2:.2f}")
            
            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** El Q3 subió en P2, los alumnos con menor rendimiento mejoraron.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** El Q3 bajó, indicando un desempeño más bajo en el 75% inferior.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** No hubo cambio en el Q3, el rendimiento inferior se mantuvo igual.")

        elif "total" in pregunta or "alumnos" in pregunta:
            p1 = estadisticas_dict['P1']['total']
            p2 = estadisticas_dict['P2']['total']

            st.sidebar.markdown("👥 **Total de alumnos con calificación registrada**")
            st.sidebar.info("Refleja cuántos estudiantes fueron evaluados en cada parcial. Las diferencias pueden deberse a inasistencias, faltas de entrega o errores en captura de datos.")
            st.sidebar.success(f"🟢 P1: {p1}  \n🔵 P2: {p2}")

            if p2 > p1:
                st.sidebar.markdown("📈 **Conclusión:** Más alumnos fueron evaluados en el segundo parcial.")
            elif p2 < p1:
                st.sidebar.markdown("📉 **Conclusión:** Menos alumnos tienen calificación en P2. Puede indicar ausencias o datos faltantes.")
            else:
                st.sidebar.markdown("➖ **Conclusión:** El número de alumnos evaluados se mantuvo igual en ambos parciales.")

        elif "pdf" in pregunta or "descargar" in pregunta:
            st.sidebar.info("📄 Puedes generar un PDF con las gráficas y estadísticas actuales usando el botón en la parte del final de las graficas.")
        else:
            st.sidebar.warning("❓ No encontré una respuesta. Intenta con: media, varianza, PDF, boxplot, etc.")
            
# ----------- Histograma  ------------------
st.markdown("## 📊 Histograma Calificaciones")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('#121212')  # fondo oscuro

for idx, parcial in enumerate(['P1', 'P2']):
    calificaciones = calificaciones_dict[parcial]
    if calificaciones.empty:
        axes[idx].set_title(f'{parcial} - Sin datos', color='white')
        axes[idx].axis('off')
        continue

    conteo, _ = np.histogram(calificaciones, bins=rango_bins)
    total = len(calificaciones)
    porcentajes = (conteo / total) * 100

    axes[idx].set_facecolor('#121212')  # fondo oscuro subplot
    barras = axes[idx].bar(rango_labels, conteo, color=[rango_colores[label] for label in rango_labels])

    # Porcentajes encima de cada barra
    for bar, pct in zip(barras, porcentajes):
        height = bar.get_height()
        axes[idx].text(bar.get_x() + bar.get_width()/2, height + 0.3,
                       f'{pct:.1f}%', ha='center', color='white', fontsize=10, fontweight='bold')

    axes[idx].set_title(f'Histograma {parcial}', color='white', fontsize=16, fontweight='bold')
    axes[idx].set_xlabel('Rango', color='white', fontsize=12)
    axes[idx].set_ylabel('Frecuencia', color='white', fontsize=12)
    axes[idx].tick_params(colors='white')  # ticks blancos

plt.tight_layout()
st.pyplot(fig)

# Aquí agregas la explicación/comparativa abajo de la gráfica
st.markdown("""
### 📋 Análisis del Histograma
- El histograma nos muestra la frecuencia de calificaciones por rango para ambos parciales.
- Puedes observar cómo se distribuyen las calificaciones en P1 y P2, y si hubo cambios en la concentración o dispersión.
""")

# Ejemplo conclusión simple con media para agregar info extra:
p1_media = estadisticas_dict['P1']['media']
p2_media = estadisticas_dict['P2']['media']

if p2_media > p1_media:
    st.success("✅ La media en P2 aumentó, lo que indica una mejora general en las calificaciones.")
elif p2_media < p1_media:
    st.warning("⚠️ La media en P2 disminuyó, lo que podría indicar un rendimiento más bajo.")
else:
    st.info("➖ La media se mantuvo estable entre ambos parciales.")


# ------------------ Gráfica de pastel -------------------
st.markdown("## 🥧 Gráficas de Pastel Calificaciones")
fig, axes = plt.subplots(1, 2, figsize=(12, 6), facecolor='#121212')
for ax in axes:
    ax.set_facecolor('#121212')  # fondo oscuro

tablas_html = []  # Para guardar las dos tablas y mostrarlas después

for idx, parcial in enumerate(['P1', 'P2']):
    calificaciones = calificaciones_dict[parcial]
    if calificaciones.empty:
        axes[idx].set_title(f'{parcial} - Sin datos', color='white')
        axes[idx].axis('off')
        tablas_html.append("")  # Para mantener índice
        continue

    ranges = pd.cut(calificaciones, bins=rango_bins, labels=rango_labels, right=False)
    conteo = ranges.value_counts(sort=False)
    valores = conteo.values
    etiquetas = conteo.index.tolist()
    colores = [rango_colores[label] for label in etiquetas]
    total = valores.sum()
    porcentajes = valores / total * 100

    # Gráfica pastel limpia
    wedges = axes[idx].pie(
        valores,
        labels=None,
        autopct=None,
        startangle=90,
        colors=colores,
        wedgeprops={'edgecolor': '#121212', 'linewidth': 2}
    )
    axes[idx].set_title(f'Pastel {parcial}', color='white', fontsize=16, fontweight='bold')

    # Tabla HTML para guardar
    tabla = "<table style='color:white; font-weight:bold;'>"
    tabla += "<tr><th style='text-align:left; padding-right:15px;'>🎨</th><th style='text-align:left; padding-right:15px;'>Rango</th><th style='text-align:right;'>%</th></tr>"
    for c, r, p in zip(colores, etiquetas, porcentajes):
        tabla += f"<tr>" \
                 f"<td><div style='width:20px; height:20px; background:{c}; border-radius:4px; box-shadow: 0 0 4px {c};'></div></td>" \
                 f"<td style='padding-left:10px;'>{r}</td>" \
                 f"<td style='text-align:right;'>{p:.1f}%</td>" \
                 f"</tr>"
    tabla += "</table>"
    tablas_html.append(tabla)

# Mostrar gráficas
plt.tight_layout()
st.pyplot(fig)

st.markdown("### 📋 Análisis de la Gráfica de Pastel")
st.markdown("""
- Las gráficas de pastel muestran la proporción de alumnos en cada rango de calificación para P1 y P2.
- Permiten visualizar fácilmente qué porcentaje de alumnos está en rangos altos, medios o bajos.
- Sirven para comparar la distribución de calificaciones entre ambos parciales y detectar mejoras o retrocesos.
""")

# Ejemplo conclusión simple basada en la proporción de aprobados (>= 60)
p1_aprobados = calificaciones_dict['P1'][calificaciones_dict['P1'] >= 60].count()
p2_aprobados = calificaciones_dict['P2'][calificaciones_dict['P2'] >= 60].count()
total_p1 = estadisticas_dict['P1']['total']
total_p2 = estadisticas_dict['P2']['total']

porc_aprobados_p1 = (p1_aprobados / total_p1)*100 if total_p1 > 0 else 0
porc_aprobados_p2 = (p2_aprobados / total_p2)*100 if total_p2 > 0 else 0

if porc_aprobados_p2 > porc_aprobados_p1:
    st.success(f"✅ La proporción de alumnos aprobados aumentó de {porc_aprobados_p1:.1f}% en P1 a {porc_aprobados_p2:.1f}% en P2.")
elif porc_aprobados_p2 < porc_aprobados_p1:
    st.warning(f"⚠️ La proporción de alumnos aprobados disminuyó de {porc_aprobados_p1:.1f}% en P1 a {porc_aprobados_p2:.1f}% en P2.")
else:
    st.info(f"➖ La proporción de alumnos aprobados se mantuvo estable en {porc_aprobados_p1:.1f}%.")
    
# ------------------ Tablas -------------------
col1, col2 = st.columns(2)
col1.markdown("#### P1")
col1.markdown(tablas_html[0], unsafe_allow_html=True)
col2.markdown("#### P2")
col2.markdown(tablas_html[1], unsafe_allow_html=True)

# Guardar las variables para el PDF
colores_pie1 = [rango_colores[label] for label in pd.cut(calificaciones_dict['P1'], bins=rango_bins, labels=rango_labels, right=False).value_counts(sort=False).index.tolist()]
etiquetas_pie1 = rango_labels
valores1 = pd.cut(calificaciones_dict['P1'], bins=rango_bins, labels=rango_labels, right=False).value_counts(sort=False).values
porcentajes_pie1 = valores1 / valores1.sum() * 100

colores_pie2 = [rango_colores[label] for label in pd.cut(calificaciones_dict['P2'], bins=rango_bins, labels=rango_labels, right=False).value_counts(sort=False).index.tolist()]
etiquetas_pie2 = rango_labels
valores2 = pd.cut(calificaciones_dict['P2'], bins=rango_bins, labels=rango_labels, right=False).value_counts(sort=False).values
porcentajes_pie2 = valores2 / valores2.sum() * 100


# ----------- Boxplot ------------------
st.markdown("## 📦 Boxplot Calificaciones")

if not grupo_df[['P1', 'P2']].dropna(how='all').empty:
    fig, ax = plt.subplots(figsize=(7, 5), facecolor='#121212')
    fig.patch.set_facecolor('#121212')

    # Boxplot detalles
    sns.boxplot(
        data=grupo_df[['P1', 'P2']],
        palette=['#ff073a', '#00ff00'],
        width=0.4,
        linewidth=2.5,
        fliersize=0,
        ax=ax
    )

    # Puntos individuales los de color blanco
    sns.stripplot(
        data=grupo_df[['P1', 'P2']],
        jitter=True,
        dodge=True,
        size=6,
        color='white',
        alpha=0.6,
        ax=ax
    )

    # Fondo y ejes
    ax.set_facecolor('#121212')
    ax.tick_params(colors='white', labelsize=12)
    ax.set_ylabel('Calificación', color='white', fontsize=13)
    ax.set_xlabel('', color='white')

    # Bordes blancos 
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(1.5)

    # Grid discreto en eje Y
    ax.yaxis.grid(True, linestyle='--', linewidth=0.7, color='gray', alpha=0.3)
    ax.set_axisbelow(True)

    st.pyplot(fig)

    st.markdown("### 📋 Análisis del Boxplot")
    st.markdown("""
    - El boxplot resume la distribución de las calificaciones, mostrando la mediana, dispersión y posibles valores atípicos.
    - La caja indica dónde está el 50% central de las calificaciones (entre Q1 y Q3).
    - Si la caja o los bigotes cambian entre P1 y P2, significa cambios en la variabilidad o concentración de calificaciones.
    """)

    # Datos relevantes para conclusión
    p1_q1 = estadisticas_dict['P1']['q1']
    p1_q3 = estadisticas_dict['P1']['q3']
    p2_q1 = estadisticas_dict['P2']['q1']
    p2_q3 = estadisticas_dict['P2']['q3']

    # Comparación simple de rango intercuartílico (IQR)
    iqr_p1 = p1_q3 - p1_q1
    iqr_p2 = p2_q3 - p2_q1

    if iqr_p2 < iqr_p1:
        st.success("✅ La dispersión (IQR) disminuyó en P2, indicando que las calificaciones se concentraron más alrededor de la mediana.")
    elif iqr_p2 > iqr_p1:
        st.warning("⚠️ La dispersión (IQR) aumentó en P2, lo que indica mayor variabilidad en las calificaciones.")
    else:
        st.info("➖ La dispersión (IQR) se mantuvo estable entre ambos parciales.")

    # Comparar medianas
    p1_mediana = estadisticas_dict['P1']['mediana']
    p2_mediana = estadisticas_dict['P2']['mediana']

    if p2_mediana > p1_mediana:
        st.success("✅ La mediana aumentó en P2, sugiriendo una mejora general en el rendimiento.")
    elif p2_mediana < p1_mediana:
        st.warning("⚠️ La mediana disminuyó en P2, indicando posible bajo rendimiento.")
    else:
        st.info("➖ La mediana se mantuvo igual entre ambos parciales.")

    # leyenda descriptiva
    with st.expander("📌 ¿Qué muestra este boxplot?"):
        st.markdown("""
        - La **línea central** representa la mediana.
        - El **cuerpo de la caja** abarca del primer al tercer cuartil (Q1 a Q3).
        - Las **líneas externas** (bigotes) muestran el rango típico.
        - Los **puntos blancos** son calificaciones individuales.
        """)
        
    with st.expander("✨ Desarrollado por el equipo 603"):
            
        st.markdown("""
        <style>
        .footer-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #ccc;
            font-size: 14px;
            margin-top: 30px;
            padding: 10px;
            animation: fadeIn 1s ease-in-out;
        }

        .footer-line {
            border: none;
            height: 1px;
            width: 80%;
            background: linear-gradient(to right, #00ffff, transparent);
            margin-bottom: 15px;
            opacity: 0.5;
        }

        .footer-list {
            list-style: none;
            padding: 0;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .footer-list li {
            position: relative;
            padding-left: 25px;
            color: #00ffff;
            font-weight: 600;
            text-shadow: 0 0 6px #00ffffaa;
            transition: all 0.3s ease;
        }

        .footer-list li::before {
            content: '💠';
            position: absolute;
            left: 0;
            color: #00ffff;
            font-size: 16px;
            animation: pulse 2s infinite;
        }

        .footer-list li:hover {
            color: #ffffff;
            text-shadow: 0 0 10px #ffffff;
            transform: translateX(5px);
        }

        .footer-links a {
            color: #00ffff;
            margin: 0 10px;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .footer-links a:hover {
            color: #ffffff;
            text-shadow: 0 0 8px #ffffff;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
            100% { opacity: 0.5; transform: scale(1); }
        }
        </style>

        <hr class='footer-line'>
        <div class='footer-container'>
            <ul class='footer-list'>
                <li>Axel Morales</li>
                <li>Itzel Taneli Hernandez Salinas</li>
                <li>Thalia Ramos Garcia</li>
                <li>Brizza Lizeht Gomez Gracia</li>
                <li>Enrique Morales del Rio</li>
            </ul>
            <div style='margin-top:15px;' class='footer-links'>
                🌐 <a href='https://github.com/equipo603' target='_blank'>GitHub</a> |
                💼 <a href='https://linkedin.com/in/equipo603' target='_blank'>LinkedIn</a> |
                🖼️ <a href='https://portafolio603.com' target='_blank'>Portafolio</a>
            </div>
            <div style='margin-top:10px;'>💻 Proyecto 2 Analisis de Calificaciones - 2025</div>
        </div>
        """, unsafe_allow_html=True)

            
else:
    st.info("📉 No hay datos suficientes para mostrar el boxplot.")
# Función para quitar emojis (¡clave para evitar errores!)
def quitar_emojis(texto):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticonos
        u"\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte y mapas
        u"\U0001F1E0-\U0001F1FF"  # banderas
        u"\U00002700-\U000027BF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA70-\U0001FAFF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', texto)

#--------------Creación del PDF sin errores de emoji----------------
def generar_pdf(calificaciones_dict, carrera, grupo, asignatura, semestre,
                colores_pies=None, etiquetas_pies=None, porcentajes_pies=None):

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    
    def poner_fondo_negro():
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(0, 0, 210, 297, 'F')

    def quitar_emojis(texto):
        return texto.encode('ascii', 'ignore').decode('ascii')

    # Primera página - encabezado y estadísticas
    pdf.add_page()
    poner_fondo_negro()
    pdf.set_text_color(0, 255, 213)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, quitar_emojis("Reporte de Calificaciones"), ln=True, align='C')

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    encabezado = f"Carrera: {carrera} | Asignatura: {asignatura} | Grupo: {grupo} | Semestre: {semestre}"
    pdf.cell(0, 10, quitar_emojis(encabezado), ln=True)

    for parcial, calificaciones in calificaciones_dict.items():
        if calificaciones.empty:
            continue
        pdf.set_text_color(0, 255, 213)
        pdf.set_font("Arial", 'B', 12)
        pdf.ln(8)
        pdf.cell(0, 10, quitar_emojis(f"Estadísticas de {parcial}"), ln=True)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", '', 11)

        moda_resultado = stats.mode(calificaciones, nan_policy='omit', keepdims=True)
        moda_valor = moda_resultado.mode[0] if len(moda_resultado.mode) > 0 else np.nan

        pdf.cell(0, 8, f"Media: {calificaciones.mean():.2f}", ln=True)
        pdf.cell(0, 8, f"Mediana: {calificaciones.median():.2f}", ln=True)
        pdf.cell(0, 8, f"Moda: {moda_valor:.2f}", ln=True)
        pdf.cell(0, 8, f"Varianza: {calificaciones.var():.2f}", ln=True)
        pdf.cell(0, 8, f"Rango: {calificaciones.max() - calificaciones.min():.2f}", ln=True)

    # Guardar gráficas como imágenes temporales
    img_paths = []
    for fig_num in plt.get_fignums():
        fig = plt.figure(fig_num)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(temp_file.name, bbox_inches='tight')
        img_paths.append(temp_file.name)

    # Intentar poner las primeras 2 gráficas juntas en una sola página, verticalmente
    if len(img_paths) >= 2:
        pdf.add_page()
        poner_fondo_negro()
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Gráficas 1 y 2", ln=True, align='C')

        max_width = 180  # casi el ancho total con margen
        max_height = 120  # la mitad aprox. de la página menos márgenes

        y_positions = [25, 25 + max_height + 10]  # arriba y abajo con separación de 10mm
        x_position = 15  # margen lateral fijo

        for i in range(2):
            img_path = img_paths[i]
            im = Image.open(img_path)
            width_px, height_px = im.size
            dpi = im.info.get('dpi', (72, 72))[0]

            width_mm = (width_px / dpi) * 25.4
            height_mm = (height_px / dpi) * 25.4

            scale = min(max_width / width_mm, max_height / height_mm, 1)

            final_width = width_mm * scale
            final_height = height_mm * scale

            pdf.image(img_path, x=x_position, y=y_positions[i], w=final_width, h=final_height)

    # Ahora la gráfica 3 (boxplot) en página nueva
    if len(img_paths) >= 3:
        pdf.add_page()
        poner_fondo_negro()
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Gráfica 3 - Boxplot", ln=True, align='C')

        img_path = img_paths[2]
        im = Image.open(img_path)
        width_px, height_px = im.size
        dpi = im.info.get('dpi', (72, 72))[0]

        width_mm = (width_px / dpi) * 25.4
        height_mm = (height_px / dpi) * 25.4

        # Escalar para que quepa casi toda la página con margen
        max_width = 180
        max_height = 250

        scale = min(max_width / width_mm, max_height / height_mm, 1)

        final_width = width_mm * scale
        final_height = height_mm * scale

        pdf.image(img_path, x=15, y=25, w=final_width, h=final_height)
        
        # Luego de las gráficas, pon leyendas si existen
        if colores_pies and etiquetas_pies and porcentajes_pies:
            pdf.set_xy(10, y_positions[1] + max_height + 5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Leyendas:", ln=True)
            pdf.set_font("Arial", '', 11)
            poner_fondo_negro()

            y_leyenda = pdf.get_y()
            ancho_cuadro = 8
            alto_cuadro = 8

            # Leyendas para las 2 gráficas
            for i in range(2):
                colores = list(colores_pies[i])
                etiquetas = list(etiquetas_pies[i])
                porcentajes = list(porcentajes_pies[i])

                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Datos Grafica {i + 1}", ln=True)
                pdf.set_font("Arial", '', 11)

                for idx, (c, etiqueta, porcentaje) in enumerate(zip(colores, etiquetas, porcentajes)):
                    x = 10
                    y = pdf.get_y() + 2

                    r, g, b = tuple(int(c.strip('#')[j:j+2], 16) for j in (0, 2, 4))
                    pdf.set_fill_color(r, g, b)
                    pdf.rect(x, y, ancho_cuadro, alto_cuadro, 'F')
                    pdf.set_xy(x + ancho_cuadro + 2, y - 2)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(60, 10, etiqueta, ln=0)
                    pdf.cell(20, 10, f"{porcentaje:.1f}%", ln=1)

                pdf.ln(5)
    else:
        # Si hay menos de 2 gráficas o no caben juntas, cada una en página individual
        for i, img in enumerate(img_paths):
            pdf.add_page()
            poner_fondo_negro()
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, quitar_emojis(f"Grafica {i + 1}"), ln=True, align='C')
            pdf.image(img, x=10, y=25, w=190)

    # Guardar y limpiar imágenes temporales
    pdf_path = os.path.join(tempfile.gettempdir(), "reporte_calificaciones.pdf")
    pdf.output(pdf_path)

    for img in img_paths:
        try:
            os.remove(img)
        except PermissionError:
            pass

    return pdf_path
# ------------------ Extraer datos pastel para PDF -------------------
colores1, etiquetas1, porcentajes1 = [], [], []
colores2, etiquetas2, porcentajes2 = [], [], []

for idx, parcial in enumerate(['P1', 'P2']):
    calificaciones = calificaciones_dict[parcial]
    if calificaciones.empty:
        continue

    ranges = pd.cut(calificaciones, bins=rango_bins, labels=rango_labels, right=False)
    conteo = ranges.value_counts(sort=False)
    valores = conteo.values
    etiquetas = conteo.index.tolist()
    colores = [rango_colores[label] for label in etiquetas]
    total = valores.sum()
    porcentajes = valores / total * 100

    if parcial == 'P1':
        colores1, etiquetas1, porcentajes1 = colores, etiquetas, porcentajes
    else:
        colores2, etiquetas2, porcentajes2 = colores, etiquetas, porcentajes

# ------------ Botón que se encarga de generar y descargar el PDF -----------------
if st.button("📥 Generar reporte PDF"):
    pdf_file = generar_pdf(
        calificaciones_dict=calificaciones_dict,
        carrera=carrera_seleccionada,
        grupo=grupo_seleccionado,
        asignatura=asignatura_seleccionada,
        semestre=semestre_seleccionado,
        colores_pies=[colores1, colores2],         # ✅ Correcto
        etiquetas_pies=[etiquetas1, etiquetas2],   # ✅ Correcto
        porcentajes_pies=[porcentajes1, porcentajes2]  # ✅ Correcto
    )

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📄 Descargar PDF",
            data=f,
            file_name="Reporte_Calificaciones.pdf",
            mime="application/pdf"
        )
