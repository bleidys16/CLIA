document.addEventListener("DOMContentLoaded", function () {
    // 1. Cargar el historial de logs automáticamente al abrir la pantalla
    cargarHistorialLogs();

    // 2. Vincular la acción al botón de inicio del Pipeline
    const btnRunEtl = document.getElementById('btn-run-etl');
    if (btnRunEtl) {
        btnRunEtl.addEventListener('click', ejecutarPipelineETL);
    }
});

// FUNCIÓN ASÍNCRONA PARA TRAER LOS LOGS DE AUDITORÍA DESDE EL BACKEND
async function cargarHistorialLogs() {
    const tableBody = document.getElementById('etl-logs-table-body');
    if (!tableBody) return;

    try {
        // Petición GET al endpoint de auditoría de tu API de Django
        const response = await fetch('/api/etl/logs/');
        if (!response.ok) throw new Error("Incapaz de recuperar las auditorías del servidor.");

        const logs = await response.json();
        tableBody.innerHTML = ''; // Limpiar el indicador visual de carga

        if (logs.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fa-solid fa-folder-open me-2"></i> No se registran ejecuciones previas del motor ETL.
                    </td>
                </tr>`;
            return;
        }

        // Iterar y pintar cada fila usando la tipografía limpia Urbanist y badges semánticos
        logs.forEach(log => {
            const fechaFormateada = new Date(log.fecha_ejecucion).toLocaleString('es-CO');

            // Badge personalizado con la paleta de colores para el estado
            const estadoBadge = log.estado === 'Exitoso' || log.estado === 'Success'
                ? '<span class="badge" style="background-color: var(--clia-wisteria); color: var(--clia-jacarta); font-weight: 600;">Completado</span>'
                : '<span class="badge bg-danger text-white">Fallido</span>';

            tableBody.innerHTML += `
                <tr>
                    <td class="fw-bold" style="color: var(--clia-jacarta);">${fechaFormateada}</td>
                    <td><i class="fa-solid fa-circle-check text-success me-1"></i> ${log.registros_procesados || 0} pac.</td>
                    <td class="text-muted"><i class="fa-solid fa-triangle-exclamation text-warning me-1"></i> ${log.errores_encontrados || 0}</td>
                    <td><small class="text-uppercase font-monospace text-secondary">${log.usuario_responsable || 'Sistema'}</small></td>
                    <td>${estadoBadge}</td>
                </tr>
            `;
        });

    } catch (error) {
        console.error("Error al renderizar la tabla de auditoría:", error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger py-4">
                    <i class="fa-solid fa-circle-xmark me-2"></i> Error de conexión con la API de logs.
                </td>
            </tr>`;
    }
}

// FUNCIÓN ASÍNCRONA PARA DISPARAR LA EJECUCIÓN CON PANDAS
async function ejecutarPipelineETL() {
    const btn = document.getElementById('btn-run-etl');
    const containerStatus = document.getElementById('etl-status-container');
    const spinner = document.getElementById('etl-spinner');
    const statusTitle = document.getElementById('etl-status-title');
    const statusDesc = document.getElementById('etl-status-desc');

    if (!btn) return;

    // Bloquear controles de inmediato para evitar que el usuario de clics repetidos
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin me-2"></i> Procesando...`;

    // Revelar el contenedor de progreso en pantalla
    containerStatus.classList.remove('d-none');
    spinner.className = "spinner-border";
    spinner.style.color = "var(--clia-blue-gray)";
    statusTitle.innerText = "Ejecutando Engine ETL...";
    statusDesc.innerText = "Pandas está extrayendo, transformando y validando la calidad del archivo clínico...";

    try {
        // Petición POST al endpoint encargado de arrancar el script de Python/Pandas
        const response = await fetch('/api/etl/run/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const resultado = await response.json();

        if (response.ok && (resultado.status === 'success' || resultado.status === 'Exitoso')) {
            // Cambiar indicador a estado de Éxito con los iconos de FontAwesome
            spinner.className = "fa-solid fa-circle-check text-success fs-4";
            spinner.style.color = "";
            statusTitle.innerText = "¡Pipeline Finalizado!";
            statusDesc.innerText = `Carga exitosa: ${resultado.total_procesados || resultado.registros_procesados} registros clínico-analíticos guardados.`;

            // Actualizar la tabla de logs automáticamente para reflejar la nueva fila sin recargar
            await cargarHistorialLogs();
        } else {
            throw new Error(resultado.message || "Fallo inesperado en las reglas de transformación de datos.");
        }

    } catch (error) {
        console.error("Error disparando el pipeline:", error);
        // Cambiar indicador a estado de Alerta Médica
        spinner.className = "fa-solid fa-triangle-exclamation text-danger fs-4";
        spinner.style.color = "";
        statusTitle.innerText = "Error en el Motor ETL";
        statusDesc.innerText = error.message || "No se pudo establecer comunicación con el pipeline de datos.";
    } finally {
        // Devolver el botón principal a su estado original
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-play me-2"></i> Iniciar Pipeline ETL`;
    }
}