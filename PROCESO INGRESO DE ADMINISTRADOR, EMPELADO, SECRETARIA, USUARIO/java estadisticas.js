const mockData = {
  sales: {
    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
    data: [12, 19, 14, 22, 24, 28]
  },
  users: {
    labels: ['Clientes', 'Propietarios', 'Agentes', 'Inactivos'],
    data: [40, 25, 20, 15]
  },
  trends: {
    labels: ['Ene', 'Feb', 'Mar', 'Abr'],
    datasets: [
      { label: '2024', data: [55, 60, 65, 70] },
      { label: '2025', data: [60, 65, 72, 80] }
    ]
  }
};

const chartColors = {
  primary: '#005792',
  secondary: '#008891',
  accent: '#f8cb2e',
  gradient: ['rgba(0, 87, 146, 0.2)', 'rgba(0, 87, 146, 0)']
};

function initializeCharts() {
  const salesCtx = document.getElementById('salesChart').getContext('2d');
  new Chart(salesCtx, {
    type: 'line',
    data: {
      labels: mockData.sales.labels,
      datasets: [{
        label: 'Publicaciones',
        data: mockData.sales.data,
        borderColor: chartColors.primary,
        backgroundColor: (() => {
          const gradient = salesCtx.createLinearGradient(0, 0, 0, 400);
          gradient.addColorStop(0, chartColors.gradient[0]);
          gradient.addColorStop(1, chartColors.gradient[1]);
          return gradient;
        })(),
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true },
        x: { grid: { display: false } }
      }
    }
  });

  const usersCtx = document.getElementById('usersChart').getContext('2d');
  new Chart(usersCtx, {
    type: 'doughnut',
    data: {
      labels: mockData.users.labels,
      datasets: [{
        data: mockData.users.data,
        backgroundColor: [chartColors.primary, chartColors.secondary, chartColors.accent, '#ccc'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      cutout: '65%'
    }
  });

  const trendsCtx = document.getElementById('trendsChart').getContext('2d');
  new Chart(trendsCtx, {
    type: 'bar',
    data: {
      labels: mockData.trends.labels,
      datasets: mockData.trends.datasets.map((dataset, index) => ({
        label: dataset.label,
        data: dataset.data,
        backgroundColor: index === 0 ? chartColors.primary : chartColors.secondary,
        borderRadius: 6
      }))
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: {
        y: { beginAtZero: true },
        x: { grid: { display: false } }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', initializeCharts);

// Activación visual en el sidebar
document.querySelectorAll('.nav-links li').forEach(item => {
  item.addEventListener('click', function () {
    document.querySelector('.nav-links li.active')?.classList.remove('active');
    this.classList.add('active');
  });
});
