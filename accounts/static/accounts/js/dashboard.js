// dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    const chartData = document.getElementById('chart-data');
    if (chartData && typeof Chart !== 'undefined') {
        const totalEmployees = parseInt(chartData.dataset.totalEmployees) || 0;
        const totalManagers = parseInt(chartData.dataset.totalManagers) || 0;
        const totalAdmins = parseInt(chartData.dataset.totalAdmins) || 0;
        const activeEmployees = parseInt(chartData.dataset.activeEmployees) || 0;
        const inactiveEmployees = parseInt(chartData.dataset.inactiveEmployees) || 0;
        const onLeaveEmployees = parseInt(chartData.dataset.onLeaveEmployees) || 0;
        const terminatedEmployees = parseInt(chartData.dataset.terminatedEmployees) || 0;
        
        // Graphique des rôles (camembert)
        const rolesChart = document.getElementById('rolesChart');
        if (rolesChart) {
            new Chart(rolesChart.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Employés', 'Managers', 'Admin RH'],
                    datasets: [{
                        data: [totalEmployees, totalManagers, totalAdmins],
                        backgroundColor: ['#3B82F6', '#10B981', '#8B5CF6'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

        // Graphique des statuts (barres)
        const statusChart = document.getElementById('statusChart');
        if (statusChart) {
            new Chart(statusChart.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['Actifs', 'Inactifs', 'En congé', 'Licenciés'],
                    datasets: [{
                        label: "Nombre d'employés",
                        data: [activeEmployees, inactiveEmployees, onLeaveEmployees, terminatedEmployees],
                        backgroundColor: ['#10B981', '#6B7280', '#F59E0B', '#EF4444'],
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1, precision: 0 }
                        }
                    }
                }
            });
        }
    }
});