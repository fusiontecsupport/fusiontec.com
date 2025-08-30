// Dashboard Charts and Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if they exist
    initializeCharts();
    
    // Auto-refresh dashboard data every 30 seconds
    setInterval(refreshDashboardData, 30000);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

function initializeCharts() {
    // Monthly Submissions Chart
    const monthlyCtx = document.getElementById('monthlyChart');
    if (monthlyCtx) {
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: monthlyChartData.labels,
                datasets: [{
                    label: 'Quote Submissions',
                    data: monthlyChartData.quotes,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Contact Submissions',
                    data: monthlyChartData.contacts,
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Monthly Submissions Trend'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    // Product Distribution Chart
    const productCtx = document.getElementById('productChart');
    if (productCtx) {
        new Chart(productCtx, {
            type: 'doughnut',
            data: {
                labels: productChartData.labels,
                datasets: [{
                    data: productChartData.data,
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c',
                        '#4facfe',
                        '#00f2fe'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Product Distribution'
                    }
                }
            }
        });
    }
    
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'bar',
            data: {
                labels: revenueChartData.labels,
                datasets: [{
                    label: 'Revenue',
                    data: revenueChartData.data,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: '#667eea',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Monthly Revenue'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Quote Status Chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Approved', 'Pending', 'Rejected', 'Other'],
                datasets: [{
                    data: [30, 25, 15, 10],
                    backgroundColor: [
                        '#198754', // Success (Approved)
                        '#ffc107', // Warning (Pending)
                        '#dc3545', // Danger (Rejected)
                        '#6c757d'  // Secondary (Other)
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Quote Status Distribution'
                    }
                }
            }
        });
    }
    
    // Weekly Activity Chart
    const weeklyCtx = document.getElementById('weeklyChart');
    if (weeklyCtx) {
        new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels: weeklyChartData.labels,
                datasets: [{
                    label: 'Quotes',
                    data: weeklyChartData.quotes,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Contacts',
                    data: weeklyChartData.contacts,
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Weekly Activity'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
}

function refreshDashboardData() {
    // Fetch updated dashboard data
    fetch('/admin/dashboard/data/')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        })
        .catch(error => {
            console.log('Dashboard refresh failed:', error);
        });
}

function updateDashboardStats(data) {
    // Update key metrics
    if (data.total_customers !== undefined) {
        document.getElementById('totalCustomers').textContent = data.total_customers;
    }
    if (data.total_quotes !== undefined) {
        document.getElementById('totalQuotes').textContent = data.total_quotes;
    }
    if (data.total_contacts !== undefined) {
        document.getElementById('totalContacts').textContent = data.total_contacts;
    }
    if (data.total_products !== undefined) {
        document.getElementById('totalProducts').textContent = data.total_products;
    }
    
    // Update monthly stats
    if (data.this_month_quotes !== undefined) {
        document.getElementById('thisMonthQuotes').textContent = data.this_month_quotes;
    }
    if (data.this_month_contacts !== undefined) {
        document.getElementById('thisMonthContacts').textContent = data.this_month_contacts;
    }
    
    // Update recent activities
    if (data.recent_quotes) {
        updateRecentActivities('recentQuotes', data.recent_quotes);
    }
    if (data.recent_contacts) {
        updateRecentActivities('recentContacts', data.recent_contacts);
    }
}

function updateRecentActivities(containerId, activities) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    activities.forEach(activity => {
        const activityHtml = `
            <div class="d-flex align-items-center mb-2">
                <div class="flex-shrink-0">
                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <i class="fas fa-${activity.icon}"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-3">
                    <div class="fw-medium">${activity.title}</div>
                    <div class="text-muted small">${activity.time}</div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', activityHtml);
    });
}

// Export functions for use in templates
window.dashboardUtils = {
    initializeCharts,
    refreshDashboardData,
    updateDashboardStats
};

// Global refresh function for the refresh button
function refreshDashboard() {
    const button = event.target.closest('button');
    const icon = button.querySelector('i');
    
    // Add spinning animation
    icon.classList.add('fa-spin');
    button.disabled = true;
    
    // Refresh data
    refreshDashboardData();
    
    // Remove spinning animation after a delay
    setTimeout(() => {
        icon.classList.remove('fa-spin');
        button.disabled = false;
    }, 2000);
}
