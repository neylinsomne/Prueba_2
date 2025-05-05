import streamlit as st
import numpy as np
import pandas as pd
import time

# Set page configuration
st.set_page_config(
    page_title="Contador de Calorías para Recetas",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stProgress > div > div > div {
        background-color: rgba(50, 205, 50, 0.8);
    }
    .ingredient-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .ingredient-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .ingredient-low {
        color: #4bb543;
        font-weight: bold;
    }
    .header-style {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'balotas' not in st.session_state:
    st.session_state.balotas = {}
if 'history' not in st.session_state:
    st.session_state.history = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Core functions from the original code
def contar(balotas, seleccionada):
    total = sum(balotas.values())
    balotas[seleccionada] = balotas[seleccionada] * 2
    for k in balotas:
        balotas[k] = balotas[k] / total
    return balotas

def movimiento(balotas, seleccionada):
    message = ""
    if balotas[seleccionada] >= 1:
        message = f"⚠️ Agregaste mucho del ingrediente {seleccionada}. Las calorías subieron más del 100%. ¡Haz de nuevo la receta!"
        n = len(balotas)
        balotas = {str(i): 1/n for i in range(1, n+1)}
    elif balotas[seleccionada] >= .75:
        message = f"✅ El ingrediente {seleccionada} mejoró el alimento. ¡Ya lo puedes comer!"
    else:
        message = "⏳ Aún no está listo el alimento, agrega más..."
    
    return balotas, message

# Function to reset application
def reset_app():
    st.session_state.balotas = {}
    st.session_state.history = []
    st.session_state.messages = []
    st.session_state.initialized = False

# App title and description
st.markdown("<h1 class='header-style'>🍽️ Contador de Calorías en tus Recetas</h1>", unsafe_allow_html=True)

with st.expander("ℹ️ Acerca de esta aplicación", expanded=not st.session_state.initialized):
    st.write("""
    Esta aplicación te permite hacer un seguimiento de las calorías en tus recetas mientras agregas ingredientes.
    
    **Cómo usar:**
    1. Ingresa la cantidad de ingredientes en tu receta
    2. Selecciona un ingrediente para agregar más cantidad
    3. Observa cómo cambia la distribución de calorías
    4. Sigue las sugerencias para preparar el alimento perfecto
    """)

# Initialize app if not already done
if not st.session_state.initialized:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Configuración inicial")
        ingredient_count = st.number_input(
            "¿Cuántos ingredientes tiene el alimento?", 
            min_value=2, 
            max_value=9, 
            value=5,
            help="Selecciona entre 2 y 9 ingredientes"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Iniciar contador", key="init_button", type="primary"):
            # Initialize the balotas with equal probabilities
            st.session_state.balotas = {str(i): 1/ingredient_count for i in range(1, ingredient_count+1)}
            st.session_state.initialized = True
            st.session_state.history.append(dict(st.session_state.balotas))
            st.session_state.messages.append("Contador inicializado con éxito. Etiqueta a cada ingrediente con un número.")
            st.rerun()
else:
    # Main dashboard when initialized
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Chart showing the current distribution using Streamlit's native chart
        st.subheader("Distribución de Calorías por Ingrediente")
        df = pd.DataFrame({
            'Ingrediente': list(st.session_state.balotas.keys()),
            'Proporción': list(st.session_state.balotas.values())
        })
        
        # Use Streamlit's native bar chart
        st.bar_chart(df.set_index('Ingrediente'))
        
        # Table with current values and status indicators
        st.subheader("Estado actual de los ingredientes")
        for ingredient, value in st.session_state.balotas.items():
            col_a, col_b, col_c = st.columns([1, 3, 1])
            with col_a:
                st.write(f"Ingrediente {ingredient}")
            with col_b:
                st.progress(min(value, 1.0))
            with col_c:
                if value >= 1.0:
                    st.markdown(f"<span class='ingredient-high'>Excesivo</span>", unsafe_allow_html=True)
                elif value >= 0.75:
                    st.markdown(f"<span class='ingredient-medium'>Óptimo</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='ingredient-low'>Insuficiente</span>", unsafe_allow_html=True)
    
    with col2:
        # Control panel for selecting ingredients
        st.subheader("Agregar ingredientes")
        
        selected_ingredient = st.selectbox(
            "Selecciona un ingrediente para agregar:",
            options=list(st.session_state.balotas.keys()),
            format_func=lambda x: f"Ingrediente {x}"
        )
        
        if st.button("Agregar este ingrediente", key="add_button", type="primary"):
            # Apply the operations
            st.session_state.balotas = contar(st.session_state.balotas, selected_ingredient)
            st.session_state.balotas, message = movimiento(st.session_state.balotas, selected_ingredient)
            
            # Save to history
            st.session_state.history.append(dict(st.session_state.balotas))
            st.session_state.messages.append(message)
            
            st.success(f"Ingrediente {selected_ingredient} actualizado")
            time.sleep(0.5)
            st.rerun()
        
        # Status messages and history
        st.subheader("Mensajes del sistema")
        status_container = st.container()
        
        with status_container:
            for message in st.session_state.messages[-3:]:
                st.info(message)
        
        # Reset button
        if st.button("Reiniciar contador", key="reset_button", type="secondary"):
            reset_app()
            st.success("¡Contador reiniciado!")
            time.sleep(0.5)
            st.rerun()
    
    # History visualization at the bottom
    if len(st.session_state.history) > 1:
        st.subheader("Historial de cambios")
        
        # Create a DataFrame for history display
        history_data = []
        
        for i, hist in enumerate(st.session_state.history):
            step_data = {'Paso': i}
            step_data.update({f"Ing. {ing}": val for ing, val in hist.items()})
            history_data.append(step_data)
        
        history_df = pd.DataFrame(history_data)
        
        # Display as a table
        st.dataframe(history_df, use_container_width=True)
        
        # Create separate line charts for each ingredient
        st.subheader("Evolución de proporciones")
        
        # Prepare data for line charts
        for ingredient in st.session_state.balotas.keys():
            values = [hist.get(ingredient, 0) for hist in st.session_state.history]
            ingredient_df = pd.DataFrame({
                'Paso': range(len(values)),
                f'Ingrediente {ingredient}': values
            })
            st.line_chart(ingredient_df.set_index('Paso'))
