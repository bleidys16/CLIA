document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem('token_acceso');
    if (!token) return;

    cargarDatosDashboard(token);

    document.getElementById('btn-refresh-dashboard')?.addEventListener('click', function() {
        cargarDatosDashboard(token);
    });
});

async function cargarDatosDashboard(token) {
    try {
        const response = await fetch('/api/etl/analytics/dashboard/', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();

        if (response.ok && !data.sistema_vacio) {
            document.getElementById('kpi-total').innerText = data.kpis.total_registros;
            document.getElementById('kpi-criticos').innerText = data.kpis.pacientes_criticos;
            document.getElementById('kpi-cronicos').innerText = `${data.kpis.pacientes_hipertensos} / ${data.kpis.pacientes_diabeticos}`;
            document.getElementById('kpi-riesgo').innerText = `${data.kpis.riesgo_promedio}%`;

            inicializarGraficaBarras(data.kpis);
            inicializarGraficaTorta(data.kpis);
            inicializarGraficaLineas(data.estadistica_descriptiva);
        }
    } catch (error) {
        console.error("Error al renderizar las analíticas de ApexCharts:", error);
    }
}

function inicializarGraficaBarras(kpis) {
    const options = {
        chart: { type: 'bar', height: 320, toolbar: { show: true } },
        plotOptions: { bar: { borderRadius: 6, distributed: true } },
        colors: ['#4267B2', '#FF4560', '#00E396', '#FEB019'],
        series: [{
            name: 'Pacientes',
            data: [kpis.total_registros, kpis.pacientes_criticos, kpis.pacientes_hipertensos, kpis.pacientes_diabeticos]
        }],
        xaxis: {
            categories: ['Base Total', 'Estado Crítico', 'Hipertensión', 'Diabetes']
        }
    };
    const chart = new ApexCharts(document.querySelector("#chart-barras"), options);
    chart.render();
}

function inicializarGraficaTorta(kpis) {
    const options = {
        chart: { type: 'donut', height: 320 },
        labels: ['Críticos', 'Estables (Resto)'],
        series: [kpis.pacientes_criticos, kpis.total_registros - kpis.pacientes_criticos],
        colors: ['#FF4560', '#00E396'],
        legend: { position: 'bottom' }
    };
    const chart = new ApexCharts(document.querySelector("#chart-torta"), options);
    chart.render();
}

function inicializarGraficaLineas(descriptiva) {
    const options = {
        chart: { type: 'line', height: 320, zoom: { enabled: true } },
        stroke: { curve: 'smooth', width: 3 },
        series: [
            { name: 'Media Edad', data: [descriptiva.edad.media, descriptiva.edad.mediana, descriptiva.edad.moda] },
            { name: 'Media Glucosa', data: [descriptiva.glucosa.media, descriptiva.glucosa.media + 10, descriptiva.glucosa.media - 10] }
        ],
        xaxis: { categories: ['Medición Central', 'Mediana Tendencia', 'Zona Moda'] },
        colors: ['#4b306b', '#00d1b2']
    };
    const chart = new ApexCharts(document.querySelector("#chart-lineas"), options);
    chart.render();
}
