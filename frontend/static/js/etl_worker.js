document.addEventListener("DOMContentLoaded", function () {
    // 1. Cargar el historial de logs automáticamente al abrir la pantalla
    cargarHistorialLogs();

    // 2. Vincular la acción al botón de inicio del Pipeline
    const btnRunEtl = document.getElementById('btn-run-etl');
    if (btnRunEtl) {
        btnRunEtl.addEventListener('click', ejecutarPipelineETL);
    }

    // 3. Vincular la acción al botón de restablecer datos
    const btnReset = document.getElementById('btn-reset-data');
    if (btnReset) {
        btnReset.addEventListener('click', resetearDataset);
    }
});

// FUNCIÓN ASÍNCRONA PARA TRAER LOS LOGS DE AUDITORÍA DESDE EL BACKEND
async function cargarHistorialLogs() {
    const tableBody = document.getElementById('etl-logs-table-body');
    if (!tableBody) return;

    try {
        const response = await fetch('/api/etl/logs/');

        // Si el backend responde un 404 o un error porque la tabla de logs no existe aún (sistema nuevo)
        if (!response.ok) {
            mostrarTablaVacia(tableBody);
            return;
        }

        const logs = await response.json();
        tableBody.innerHTML = '';

        if (!logs || logs.length === 0) {
            mostrarTablaVacia(tableBody);
            return;
        }

        // Iterar y pintar cada fila si existen datos
        logs.forEach(log => {
            const fechaFormateada = new Date(log.fecha_ejecucion).toLocaleString('es-CO');
            const estadoBadge = log.estado === 'Exitoso' || log.estado === 'Success'
                ? '<span class="badge" style="background-color: var(--clia-wisteria); color: var(--clia-jacarta); font-weight: 600;">Completado</span>'
                : '<span class="badge bg-danger text-white">Fallido</span>';

            tableBody.innerHTML += `
                <tr>
                    <td class="fw-bold" style="color: var(--clia-jacarta);">${fechaFormateada}</td>
                    <td><i class="fa-solid fa-circle-check text-success me-1"></i> ${log.registros_procesados || 0}</td>
                    <td class="text-muted">${log.tiempo_ejecucion ? log.tiempo_ejecucion.toFixed(2) + 's' : '—'}</td>
                    <td><small class="text-uppercase font-monospace text-secondary">${log.usuario_responsable || 'Sistema'}</small></td>
                    <td>${estadoBadge}</td>
                </tr>
            `;
        });

    } catch (error) {
        console.error("Error al renderizar la tabla de auditoría:", error);
        // En lugar de romper la UI con un error crítico, asumimos un estado inicial sin cargas
        mostrarTablaVacia(tableBody);
    }
}

// Función auxiliar para mantener la consistencia visual del estado vacío
function mostrarTablaVacia(contenedor) {
    contenedor.innerHTML = `
        <tr>
            <td colspan="5" class="text-center text-muted py-4" style="font-family: 'Urbanist', sans-serif;">
                <i class="fa-solid fa-folder-open me-2" style="color: var(--clia-wisteria);"></i> 
                No se registran ejecuciones previas. El sistema está listo para recibir el primer dataset.
            </td>
        </tr>`;
}

// FUNCIÓN ASÍNCRONA PARA DISPARAR LA EJECUCIÓN CON PANDAS ENVIANDO EL CSV
async function ejecutarPipelineETL() {
    const btn = document.getElementById('btn-run-etl');
    const fileInput = document.getElementById('fileInput');
    const containerStatus = document.getElementById('etl-status-container');
    const spinner = document.getElementById('etl-spinner');
    const statusTitle = document.getElementById('etl-status-title');
    const statusDesc = document.getElementById('etl-status-desc');

    if (!btn || !fileInput || fileInput.files.length === 0) {
        alert("Por favor, selecciona un archivo CSV antes de iniciar el proceso.");
        return;
    }

    // Bloquear controles inmediato
    btn.disabled = true;
    // Dejamos el texto del botón fijo, la animación va en el contenedor de estado

    containerStatus.classList.remove('d-none');
    spinner.className = "fa-solid fa-gears fa-spin fs-2";
    spinner.style.color = "var(--clia-jacarta)";
    statusTitle.innerText = "Ejecutando Engine ETL...";
    statusDesc.innerText = "Pandas está extrayendo, transformando y validando la calidad del archivo clínico...";

    // Preparar el archivo físico para mandarlo por HTTP Multipart
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const data = await new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/etl/run/', true);

            const token = localStorage.getItem('token_acceso');
            if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);

            xhr.onload = function () {
                try {
                    const d = JSON.parse(xhr.responseText);
                    if (xhr.status >= 200 && xhr.status < 300 && (d.status === 'success' || d.status === 'Exitoso')) {
                        resolve(d);
                    } else {
                        reject(new Error(d.message || 'Error en el servidor'));
                    }
                } catch (e) {
                    reject(new Error('Respuesta inválida del servidor'));
                }
            };

            xhr.onerror = function () {
                reject(new Error('Error de conexión con el servidor'));
            };

            xhr.send(formData);
        });

        spinner.className = "fa-solid fa-circle-check text-success fs-2";
        spinner.style.color = "";
        statusTitle.innerText = "¡Pipeline Finalizado!";
        statusDesc.innerText = `Carga exitosa: ${data.total_procesados || data.registros_procesados || 0} registros clínico-analíticos guardados.`;

        fileInput.value = '';
        document.getElementById('file-info-container').classList.add('d-none');

        await cargarHistorialLogs();

    } catch (error) {
        console.error("Error disparando el pipeline:", error);
        spinner.className = "fa-solid fa-shield-virus text-danger fs-2";
        spinner.style.color = "";
        statusTitle.innerText = "Error en el Motor ETL";
        statusDesc.innerText = error.message || "No se pudo establecer comunicación con el pipeline de datos.";
    } finally {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-play me-2"></i> Iniciar Pipeline ETL`;
    }
}

// FUNCIÓN ASÍNCRONA PARA RESTABLECER EL DATASET (ELIMINAR DATOS)
async function resetearDataset() {
    const btnReset = document.getElementById('btn-reset-data');
    if (!btnReset) return;

    const confirmacion = confirm("¿Estás seguro de que deseas restablecer el dataset? Se eliminarán todos los pacientes y el historial de cargas.");
    if (!confirmacion) return;

    btnReset.disabled = true;
    btnReset.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin me-2"></i> Restableciendo...`;

    const csrfToken = document.cookie.split('; ').find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
    try {
        const response = await fetch('/api/etl/reset/', {
            method: 'DELETE',
            headers: { 'X-CSRFToken': csrfToken }
        });
        const resultado = await response.json();

        if (response.ok && resultado.status === 'success') {
            alert(resultado.message);
            await cargarHistorialLogs();
            // Redirigir al dashboard que ahora mostrará pantalla de bienvenida
            window.location.href = '/dashboard/';
        } else {
            throw new Error(resultado.message || "Error al restablecer datos.");
        }
    } catch (error) {
        console.error("Error al restablecer:", error);
        alert("Error: " + error.message);
    } finally {
        btnReset.disabled = false;
        btnReset.innerHTML = `<i class="fa-solid fa-rotate-left me-2"></i> Restablecer Dataset`;
    }
}