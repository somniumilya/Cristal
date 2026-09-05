import streamlit as st
import numpy as np
import matplotlib.colors as mcolors
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración inicial de la página
st.set_page_config(page_title="Sistemas Cristalinos 3D", layout="wide")

st.title("🔮 Sistemas Cristalinos 3D - Dashboard Interactivo")
st.write("Explora las 7 estructuras cristalinas y sus parámetros geométricos.")

# ============================================================================
# CLASE Y DEFINICIÓN DE SISTEMAS
# ============================================================================
class SistemaCristalino:
    def __init__(self, nombre, parametros, simbolo, ejes_descripcion):
        self.nombre = nombre
        self.parametros = parametros
        self.simbolo = simbolo
        self.ejes_descripcion = ejes_descripcion
        self.color = None
        self.puntos, self.aristas = self.generar_geometria()
    
    def generar_geometria(self):
        if self.nombre == "Hexagonal":
            a, _, c, _, _, _ = self.parametros
            angulos = np.linspace(0, 2*np.pi, 7)[:-1]
            base_inf = np.array([[a * np.cos(ang), a * np.sin(ang), 0] for ang in angulos])
            base_sup = np.array([[a * np.cos(ang), a * np.sin(ang), c] for ang in angulos])
            vertices = np.vstack([base_inf, base_sup])
            aristas = []
            for i in range(6):
                aristas.append((i, (i + 1) % 6))
                aristas.append((i + 6, ((i + 1) % 6) + 6))
                aristas.append((i, i + 6))
            return vertices, aristas

        a, b, c, alpha, beta, gamma = self.parametros
        alpha_r, beta_r, gamma_r = np.radians(alpha), np.radians(beta), np.radians(gamma)
        
        v1 = np.array([a, 0, 0])
        v2 = np.array([b * np.cos(gamma_r), b * np.sin(gamma_r), 0])
        v3 = np.array([
            c * np.cos(beta_r),
            c * (np.cos(alpha_r) - np.cos(beta_r) * np.cos(gamma_r)) / np.sin(gamma_r),
            c * np.sqrt(max(0, 1 - np.cos(alpha_r)**2 - np.cos(beta_r)**2 - np.cos(gamma_r)**2 
                        + 2 * np.cos(alpha_r) * np.cos(beta_r) * np.cos(gamma_r))) / np.sin(gamma_r)
        ])
        
        vertices = [i * v1 + j * v2 + k * v3 for i in [0, 1] for j in [0, 1] for k in [0, 1]]
        aristas = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]
        return np.array(vertices), aristas

SISTEMAS = {
    "Cúbico": SistemaCristalino("Cúbico", [1, 1, 1, 90, 90, 90], "c", "a = b = c, α = β = γ = 90°"),
    "Tetragonal": SistemaCristalino("Tetragonal", [1.2, 1.2, 2.0, 90, 90, 90], "t", "a = b ≠ c, α = β = γ = 90°"),
    "Ortorrómbico": SistemaCristalino("Ortorrómbico", [1.0, 1.5, 2.0, 90, 90, 90], "o", "a ≠ b ≠ c, α = β = γ = 90°"),
    "Monoclínico": SistemaCristalino("Monoclínico", [1.2, 1.0, 1.8, 90, 115, 90], "m", "a ≠ b ≠ c, α = γ = 90°, β ≠ 90°"),
    "Triclínico": SistemaCristalino("Triclínico", [1.0, 1.3, 1.7, 75, 100, 110], "a", "a ≠ b ≠ c, α ≠ β ≠ γ ≠ 90°"),
    "Hexagonal": SistemaCristalino("Hexagonal", [1.2, 1.2, 2.0, 90, 90, 120], "h", "a = b ≠ c, α = β = 90°, γ = 120°"),
    "Romboédrico": SistemaCristalino("Romboédrico", [1.2, 1.2, 1.2, 80, 80, 80], "r", "a = b = c, α = β = γ ≠ 90°")
}

colores = list(mcolors.TABLEAU_COLORS.values())
for i, (nombre, sistema) in enumerate(SISTEMAS.items()):
    sistema.color = colores[i % len(colores)]

# ============================================================================
# RENDERIZADO EN STREAMLIT
# ============================================================================
fig = make_subplots(
    rows=2, cols=4,
    specs=[[{'type': 'scene'}, {'type': 'scene'}, {'type': 'scene'}, {'type': 'scene'}],
           [{'type': 'scene'}, {'type': 'scene'}, {'type': 'scene'}, {'type': 'scene'}]],
    subplot_titles=[f"<b>{s}</b><br><sub>{SISTEMAS[s].ejes_descripcion}</sub>" for s in SISTEMAS.keys()]
)

for i, (nombre, sistema) in enumerate(SISTEMAS.items(), 1):
    row, col = (i - 1) // 4 + 1, (i - 1) % 4 + 1
    vertices, aristas = sistema.puntos, sistema.aristas
    
    for j, k in aristas:
        fig.add_trace(go.Scatter3d(
            x=[vertices[j][0], vertices[k][0]],
            y=[vertices[j][1], vertices[k][1]],
            z=[vertices[j][2], vertices[k][2]],
            mode='lines', line=dict(color=sistema.color, width=4),
            showlegend=False, hoverinfo='none'
        ), row=row, col=col)
    
    fig.add_trace(go.Scatter3d(
        x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
        mode='markers', marker=dict(size=5, color=sistema.color),
        showlegend=False
    ), row=row, col=col)

fig.update_layout(height=800, showlegend=False, margin=dict(l=10, r=10, t=40, b=10))

# Muestra el gráfico interactivo de Plotly directamente en Streamlit
st.plotly_chart(fig, use_container_width=True)
