import matplotlib.pyplot as plt
import numpy as np
import io
import imageio.v2 as imageio
import json
from flask import send_file

# --- NUEVO: Animación temporal de la evolución de especies (GIF) ---
@app.route('/evolution_gif')
def evolution_gif():
    """
    Devuelve un GIF animado de la evolución temporal de una o varias especies.
    Parámetros GET:
        species: lista separada por comas (opcional, por defecto todas)
        duration: duración total en segundos (opcional, por defecto 5)
    """

    evo_path = os.path.join(RESULTS_DIR, 'pollution_evolution.json')
    if not os.path.exists(evo_path):
        return "No evolution data", 404
    with open(evo_path, 'r', encoding='utf-8') as f:
        evo_data = json.load(f)
    steps = evo_data.get('steps', [])
    species_data = evo_data.get('species', {})
    # Selección de especies
    req_species = request.args.get('species')
    if req_species:
        sel_species = [s for s in req_species.split(',') if s in species_data]
        if not sel_species:
            sel_species = list(species_data.keys())
    else:
        sel_species = list(species_data.keys())
    # Duración total
    duration = float(request.args.get('duration', 5))
    n_frames = len(steps)
    images = []
    for i in range(n_frames):
        plt.figure(figsize=(7,4))
        for sp in sel_species:
            vals = species_data[sp][:i+1]
            plt.plot(steps[:i+1], vals, label=sp)
        plt.xlabel('Paso temporal')
        plt.ylabel('Concentración media')
        plt.title('Evolución temporal de especies')
        plt.legend()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        images.append(imageio.imread(buf))
    gif_buf = io.BytesIO()
    imageio.mimsave(gif_buf, images, format='GIF', duration=duration/n_frames)
    gif_buf.seek(0)
    return send_file(gif_buf, mimetype='image/gif', as_attachment=True, download_name='evolution.gif')
"""
WebApp avanzada para simulación y análisis técnico de contaminación urbana.
Permite lanzar simulaciones, subir archivos, guardar configuraciones, analizar resultados y monitorizar recursos.
Autor: Mario Díaz Gómez (TFG Ingeniería Informática)
"""

import os
import threading
import numpy as np
import psutil
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from webapp_memory import memory
import time
import json

app = Flask(__name__)

# Configuración de la app y subida de archivos
app.secret_key = 'supersecretkey'  # Cambia esto en producción
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {'sumocfg', 'xml', 'gz', 'csv', 'json', 'log'}

# Ruta base de resultados
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Página principal: muestra el formulario, historial de configuraciones y resultados recientes.
    """
    configs = memory.get_configs()[::-1][:10]  # Últimas 10 configuraciones
    return render_template('index.html', configs=configs)

@app.route('/run_simulation', methods=['POST'])
def run_simulation_api():
    """
    Lanza una simulación en un hilo, guarda la configuración y monitoriza recursos.
    """
    from main import run_simulation
    config = request.json if request.is_json else request.form.to_dict()
    # Guardar configuración antes de lanzar
    memory.save_config(config)
    def run_and_save():
        # Medir recursos antes y después
        cpu_start = psutil.cpu_percent(interval=None)
        mem_start = psutil.virtual_memory().used
        t0 = time.time()
        run_simulation(config)
        t1 = time.time()
        cpu_end = psutil.cpu_percent(interval=None)
        mem_end = psutil.virtual_memory().used
        stats = {
            'cpu_percent_start': cpu_start,
            'cpu_percent_end': cpu_end,
            'mem_used_start_MB': mem_start // 1024 // 1024,
            'mem_used_end_MB': mem_end // 1024 // 1024,
            'duration_sec': t1 - t0
        }
        memory.save_config(config, stats=stats)
    threading.Thread(target=run_and_save).start()
    return jsonify({'status': 'Simulación lanzada'})

@app.route('/results')
def list_results():
    """
    Lista todos los archivos de resultados relevantes (CSV, VTK, MP4, logs).
    """
    files = [f for f in os.listdir(RESULTS_DIR) if f.startswith('pollution_grid') or f.endswith(('.mp4', '.csv', '.vtk', '.log'))]
    return jsonify({'files': files})

@app.route('/download/<filename>')
def download_file(filename):
    """
    Permite descargar cualquier archivo de resultados generado por la simulación.
    """
    path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(path):
        return "Archivo no encontrado", 404
    return send_file(path, as_attachment=True)

@app.route('/heatmap/<species>/<step>')
def heatmap(species, step):
    """
    Devuelve un heatmap PNG de la concentración de una especie en un paso dado.
    """
    import matplotlib.pyplot as plt
    grid_path = os.path.join(RESULTS_DIR, f'pollution_grid_{species}_{step}.csv')
    if not os.path.exists(grid_path):
        return "Grid no encontrado", 404
    grid = np.loadtxt(grid_path, delimiter=',')
    import io
    buf = io.BytesIO()
    plt.figure(figsize=(6,5))
    plt.imshow(grid, cmap='hot', origin='lower')
    plt.colorbar(label='Concentración')
    plt.title(f'Heatmap {species} (step {step})')
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# --- NUEVO: Subida de archivos para escenarios y configuraciones ---
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Permite subir archivos de configuración SUMO, escenarios, etc.
    """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        flash('Archivo subido correctamente')
        return jsonify({'status': 'Archivo subido', 'filename': filename})
    else:
        return jsonify({'status': 'Tipo de archivo no permitido'}), 400

# --- NUEVO: Consulta de configuraciones y estadísticas guardadas ---
@app.route('/history')
def history():
    """
    Devuelve el historial de configuraciones y estadísticas de simulación.
    """
    configs = memory.get_configs()[::-1]
    return jsonify({'history': configs})

# --- NUEVO: Consulta de estadísticas técnicas y recursos computacionales ---
@app.route('/stats')
def stats():
    """
    Devuelve estadísticas técnicas de la última simulación y recursos actuales.
    """
    # Última configuración con stats
    configs = memory.get_configs()
    last_stats = None
    for entry in reversed(configs):
        if entry.get('stats'):
            last_stats = entry['stats']
            break
    # Recursos actuales
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()
    return jsonify({
        'last_simulation_stats': last_stats,
        'current_cpu_percent': cpu,
        'current_mem_used_MB': mem.used // 1024 // 1024,
        'current_mem_total_MB': mem.total // 1024 // 1024
    })

# --- NUEVO: Análisis automático de logs y resultados (timing, cuellos de botella, etc) ---
@app.route('/analysis')
def analysis():
    """
    Devuelve análisis técnico avanzado de la última simulación (timing, gráficos, resumen).
    """
    import src.modules.timing_analysis as timing_analysis
    import io
    import base64
    # Ejecutar análisis y capturar gráficos como imágenes base64
    buf = io.StringIO()
    try:
        timing_analysis.analyze_timing_log()
        # Leer imágenes generadas y devolver como base64
        images = {}
        for fname in [
            'simulation_timing_overview.png',
            'simulation_timing_percentage_overview.png',
            'update_time_histogram.png',
            'timing_components_boxplot.png',
            'smoothed_timing_overview.png',
            'update_time_bottlenecks.png'
        ]:
            img_path = os.path.join(RESULTS_DIR, fname)
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    images[fname] = base64.b64encode(f.read()).decode('utf-8')
        return jsonify({'analysis': 'ok', 'images': images})
    except Exception as e:
        return jsonify({'analysis': 'error', 'error': str(e)})

# --- NUEVO: Endpoint para visualización en tiempo real del heatmap actual de una especie ---
@app.route('/frame/<species>')
def frame(species):
    """
    Devuelve el heatmap actual de la especie indicada como imagen PNG (para visualización en tiempo real).
    """
    import matplotlib.pyplot as plt
    import io
    import numpy as np
# --- NUEVO: Evolución temporal de una especie (media por paso) ---
@app.route('/evolution/<species>')
def evolution(species):
    """
    Devuelve la evolución temporal (media por paso) de la especie indicada en formato JSON.
    """
    # Buscar todos los archivos CSV de la especie
    files = [f for f in os.listdir(RESULTS_DIR) if f.startswith(f'pollution_grid_{species}_') and f.endswith('.csv')]
    if not files:
        return jsonify({'error': 'No hay datos para la especie'}), 404
    # Ordenar por step
    files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    evolution = []
    steps = []
    for f in files:
        grid = np.loadtxt(os.path.join(RESULTS_DIR, f), delimiter=',')
        mean_val = float(np.mean(grid))
        step = int(f.split('_')[-1].split('.')[0])
        evolution.append(mean_val)
        steps.append(step)
    return jsonify({'species': species, 'steps': steps, 'values': evolution})


# --- NUEVO: Comparativa de evolución temporal de todas las especies (usando JSON si existe) ---
@app.route('/compare')
def compare():
    """
    Devuelve la evolución temporal de todas las especies detectadas (media por paso) para comparación.
    Si existe pollution_evolution.json, lo usa para máxima eficiencia.
    """
    import json
    evo_path = os.path.join(RESULTS_DIR, 'pollution_evolution.json')
    if os.path.exists(evo_path):
        with open(evo_path, 'r', encoding='utf-8') as f:
            evo_data = json.load(f)
        steps = evo_data.get('steps', [])
        species_data = evo_data.get('species', {})
        data = {}
        for sp, vals in species_data.items():
            data[sp] = {'steps': steps, 'values': vals}
        return jsonify(data)
    # Fallback: reconstruir desde CSVs (antiguo)
    files = [f for f in os.listdir(RESULTS_DIR) if f.startswith('pollution_grid_') and f.endswith('.csv')]
    if not files:
        return jsonify({'error': 'No hay datos'}), 404
    species_set = set(f.split('_')[2] for f in files)
    data = {}
    for species in species_set:
        sp_files = [f for f in files if f.split('_')[2] == species]
        sp_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        values = []
        steps = []
        for f in sp_files:
            grid = np.loadtxt(os.path.join(RESULTS_DIR, f), delimiter=',')
            mean_val = float(np.mean(grid))
            step = int(f.split('_')[-1].split('.')[0])
            values.append(mean_val)
            steps.append(step)
        data[species] = {'steps': steps, 'values': values}
    return jsonify(data)
    # Buscar el último archivo CSV de la especie (más reciente)
    files = [f for f in os.listdir(RESULTS_DIR) if f.startswith(f'pollution_grid_{species}_') and f.endswith('.csv')]
    if not files:
        return "No hay datos aún", 404
    # Seleccionar el de mayor step
    files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]), reverse=True)
    grid_path = os.path.join(RESULTS_DIR, files[0])
    grid = np.loadtxt(grid_path, delimiter=',')
    buf = io.BytesIO()
    plt.figure(figsize=(6,5))
    plt.imshow(grid, cmap='hot', origin='lower')
    plt.colorbar(label='Concentración')
    plt.title(f'Heatmap {species} (step {files[0].split("_")[-1].split(".")[0]})')
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    # Ejecutar la WebApp en modo debug para desarrollo
    app.run(debug=True, port=5000)
