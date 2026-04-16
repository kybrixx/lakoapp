// Chart Utilities for Lako
class ChartManager {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#0f5c2f',
            secondary: '#5a6e5a',
            success: '#10b981',
            warning: '#eab308',
            danger: '#dc2626',
            info: '#3b82f6',
            purple: '#8b5cf6',
            orange: '#f97316'
        };
    }

    createChart(ctx, type, data, options = {}) {
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, padding: 20 }
                }
            }
        };
        
        return new Chart(ctx, {
            type: type,
            data: data,
            options: { ...defaultOptions, ...options }
        });
    }

    createLineChart(ctx, labels, datasets, options = {}) {
        return this.createChart(ctx, 'line', { labels, datasets }, {
            ...options,
            elements: { line: { tension: 0.4 } }
        });
    }

    createBarChart(ctx, labels, datasets, options = {}) {
        return this.createChart(ctx, 'bar', { labels, datasets }, options);
    }

    createPieChart(ctx, labels, data, options = {}) {
        return this.createChart(ctx, 'pie', {
            labels,
            datasets: [{
                data,
                backgroundColor: Object.values(this.colors)
            }]
        }, options);
    }

    createDoughnutChart(ctx, labels, data, options = {}) {
        return this.createChart(ctx, 'doughnut', {
            labels,
            datasets: [{
                data,
                backgroundColor: Object.values(this.colors)
            }]
        }, options);
    }

    createRadarChart(ctx, labels, datasets, options = {}) {
        return this.createChart(ctx, 'radar', { labels, datasets }, options);
    }

    createTrafficChart(ctx, hourlyData) {
        const labels = hourlyData.map(h => `${h.hour}:00`);
        const data = hourlyData.map(h => h.count);
        
        return this.createLineChart(ctx, labels, [{
            label: 'Foot Traffic',
            data: data,
            borderColor: this.colors.primary,
            backgroundColor: this.colors.primary + '20',
            fill: true,
            tension: 0.4
        }]);
    }

    createRatingChart(ctx, ratings) {
        const labels = ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'];
        const data = [
            ratings[5] || 0,
            ratings[4] || 0,
            ratings[3] || 0,
            ratings[2] || 0,
            ratings[1] || 0
        ];
        
        return this.createBarChart(ctx, labels, [{
            label: 'Reviews',
            data: data,
            backgroundColor: [
                '#10b981', '#84cc16', '#eab308', '#f97316', '#dc2626'
            ]
        }], {
            indexAxis: 'y',
            plugins: { legend: { display: false } }
        });
    }

    createGrowthChart(ctx, labels, userData, vendorData) {
        return this.createLineChart(ctx, labels, [
            {
                label: 'Users',
                data: userData,
                borderColor: this.colors.primary,
                backgroundColor: 'transparent'
            },
            {
                label: 'Vendors',
                data: vendorData,
                borderColor: this.colors.warning,
                backgroundColor: 'transparent'
            }
        ]);
    }

    createAnalyticsChart(ctx, metrics) {
        return this.createRadarChart(ctx, 
            ['Views', 'Reviews', 'Rating', 'Products', 'Traffic'],
            [{
                label: 'Performance',
                data: [
                    metrics.views || 0,
                    metrics.reviews || 0,
                    metrics.rating || 0,
                    metrics.products || 0,
                    metrics.traffic || 0
                ],
                backgroundColor: this.colors.primary + '40',
                borderColor: this.colors.primary,
                pointBackgroundColor: this.colors.primary
            }]
        );
    }

    destroyChart(id) {
        if (this.charts[id]) {
            this.charts[id].destroy();
            delete this.charts[id];
        }
    }

    destroyAll() {
        Object.keys(this.charts).forEach(id => this.destroyChart(id));
    }

    updateChart(id, data) {
        if (this.charts[id]) {
            this.charts[id].data = data;
            this.charts[id].update();
        }
    }
}

const chartManager = new ChartManager();

// Helper function for quick chart creation
function createChart(elementId, type, data, options = {}) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return null;
    return chartManager.createChart(ctx, type, data, options);
}