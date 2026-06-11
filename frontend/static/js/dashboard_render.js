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
        const [responseKpi, responsePacientes] = await Promise.all([
            fetch('/api/etl/analytics/dashboard/', {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch('/api/etl/pacientes/', {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}` }
            })
        ]);

        const dataKpi = await responseKpi.json();
        let pacientes = [];
        if (responsePacientes.ok) {
            pacientes = await responsePacientes.json();
        }

        if (responseKpi.ok && !dataKpi.sistema_vacio) {
            document.getElementById('kpi-total').innerText = dataKpi.kpis.total_registros;
            document.getElementById('kpi-criticos').innerText = dataKpi.kpis.pacientes_criticos;
            document.getElementById('kpi-edad').innerText = dataKpi.estadistica_descriptiva.edad.media;
            document.getElementById('kpi-riesgo').innerText = `${dataKpi.kpis.riesgo_promedio}%`;

            if (pacientes.length > 0) {
                inicializarGraficaBarras(pacientes);
                inicializarGraficaLineas(pacientes);
                inicializarGraficaTorta(pacientes);
            }
        }
    } catch (error) {
        console.error("Error al renderizar las analíticas de ApexCharts:", error);
    }
}

// Global chart instances to destroy them before re-rendering
let chartBarras = null;
let chartLineas = null;
let chartTorta = null;

function inicializarGraficaBarras(pacientes) {
    let r1=0, r2=0, r3=0, r4=0;
    pacientes.forEach(p => {
        if (p.edad < 30) r1++;
        else if (p.edad <= 45) r2++;
        else if (p.edad <= 60) r3++;
        else r4++;
    });

    const options = {
        chart: { type: 'bar', height: 320, toolbar: { show: true } },
        plotOptions: { bar: { borderRadius: 6, distributed: true } },
        colors: ['#4267B2', '#FF4560', '#00E396', '#FEB019'],
        series: [{
            name: 'Pacientes',
            data: [r1, r2, r3, r4]
        }],
        xaxis: {
            categories: ['Menores de 30', '30 a 45', '46 a 60', 'Mayores de 60']
        }
    };
    if (chartBarras) chartBarras.destroy();
    chartBarras = new ApexCharts(document.querySelector("#chart-barras"), options);
    chartBarras.render();
}

function inicializarGraficaLineas(pacientes) {
    const ageGroups = {
        '<30': { ps: 0, glu: 0, fc: 0, count: 0 },
        '30-45': { ps: 0, glu: 0, fc: 0, count: 0 },
        '46-60': { ps: 0, glu: 0, fc: 0, count: 0 },
        '>60': { ps: 0, glu: 0, fc: 0, count: 0 }
    };

    pacientes.forEach(p => {
        let key = '';
        if (p.edad < 30) key = '<30';
        else if (p.edad <= 45) key = '30-45';
        else if (p.edad <= 60) key = '46-60';
        else key = '>60';

        ageGroups[key].ps += (p.presion_sistolica || 0);
        ageGroups[key].glu += (p.glucosa || 0);
        ageGroups[key].fc += (p.frecuencia_cardiaca || 0); // Note: Assuming model has it or use a default if null
        ageGroups[key].count++;
    });

    const getAvg = (key, prop) => ageGroups[key].count ? Math.round(ageGroups[key][prop] / ageGroups[key].count) : 0;

    const options = {
        chart: { type: 'line', height: 320, zoom: { enabled: true } },
        stroke: { curve: 'smooth', width: 3 },
        series: [
            { name: 'Presión Sistólica', data: [getAvg('<30', 'ps'), getAvg('30-45', 'ps'), getAvg('46-60', 'ps'), getAvg('>60', 'ps')] },
            { name: 'Glucosa', data: [getAvg('<30', 'glu'), getAvg('30-45', 'glu'), getAvg('46-60', 'glu'), getAvg('>60', 'glu')] },
            // If frecuencia_cardiaca is not populated in the API, it will be 0. We'll leave it as requested.
            { name: 'Frec. Cardíaca', data: [getAvg('<30', 'fc'), getAvg('30-45', 'fc'), getAvg('46-60', 'fc'), getAvg('>60', 'fc')] }
        ],
        xaxis: { categories: ['< 30', '30-45', '46-60', '> 60'] },
        colors: ['#4b306b', '#00d1b2', '#FF4560']
    };
    if (chartLineas) chartLineas.destroy();
    chartLineas = new ApexCharts(document.querySelector("#chart-lineas"), options);
    chartLineas.render();
}

function inicializarGraficaTorta(pacientes) {
    let hombres = 0, mujeres = 0;
    pacientes.forEach(p => {
        if (p.sexo && p.sexo.toLowerCase() === 'femenino' || p.sexo === 'f') mujeres++;
        else hombres++;
    });

    const options = {
        chart: { type: 'donut', height: 320 },
        labels: ['Hombres', 'Mujeres'],
        series: [hombres, mujeres],
        colors: ['#4267B2', '#FF4560'],
        legend: { position: 'bottom' }
    };
    if (chartTorta) chartTorta.destroy();
    chartTorta = new ApexCharts(document.querySelector("#chart-torta"), options);
    chartTorta.render();
}
