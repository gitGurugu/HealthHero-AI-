/**
 * HealthHero AI - 健康数据大屏管理器
 */
class HealthDashboard {
    constructor() {
        this.baseURL = 'http://localhost:8000/api/v1';
        this.currentUser = null;
        this.currentPeriod = '30d';
        this.charts = {};
        this.refreshInterval = null;
        
        this.init();
    }

    async init() {
        // 首先获取当前登录用户信息
        this.loadCurrentUser();
        this.setupEventListeners();
        this.startTimeDisplay();
        await this.loadInitialData();
        this.startAutoRefresh();
    }

    loadCurrentUser() {
        // 从localStorage获取当前登录用户信息
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (!user.id) {
            this.showError('用户未登录，请先登录');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
            return;
        }
        
        this.currentUser = user.id;
        console.log('当前用户ID:', this.currentUser);
        
        // 隐藏用户选择器，因为只显示当前用户数据
        const userSelect = document.getElementById('userSelect');
        if (userSelect) {
            userSelect.style.display = 'none';
        }
        
        // 更新页面标题显示用户名
        this.updatePageTitle(user.username);
    }

    updatePageTitle(username) {
        const headerTitle = document.querySelector('.dashboard-header h1');
        if (headerTitle) {
            headerTitle.textContent = `${username} 的健康数据监控`;
        }
    }

    setupEventListeners() {
        // 时间周期变化
        document.getElementById('periodSelect').addEventListener('change', (e) => {
            this.currentPeriod = e.target.value;
            this.refreshAllData();
        });

        // 图表控制按钮
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const metric = e.target.dataset.metric;
                const distribution = e.target.dataset.distribution;
                
                if (metric) {
                    this.switchTrendMetric(e.target, metric);
                } else if (distribution) {
                    this.switchDistribution(e.target, distribution);
                }
            });
        });
    }

    startTimeDisplay() {
        const updateTime = () => {
            const now = new Date();
            const timeString = now.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            document.getElementById('currentTime').textContent = timeString;
        };
        
        updateTime();
        setInterval(updateTime, 1000);
    }

    startAutoRefresh() {
        // 每5分钟自动刷新数据
        this.refreshInterval = setInterval(() => {
            this.refreshAllData();
        }, 5 * 60 * 1000);
    }

    async loadInitialData() {
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadTrendData('weight'),
                this.loadTrendData('systolic'),
                this.loadDistribution('bmi_category'),
                this.loadUsersSummary()
            ]);
        } catch (error) {
            this.showError('加载初始数据失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async refreshAllData() {
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadTrendData(this.getCurrentTrendMetric('weight')),
                this.loadTrendData(this.getCurrentTrendMetric('blood-pressure')),
                this.loadDistribution(this.getCurrentDistribution()),
                this.loadUsersSummary()
            ]);
        } catch (error) {
            this.showError('刷新数据失败: ' + error.message);
        }
    }

    async loadOverviewStats() {
        try {
            // 始终使用当前用户ID
            const url = `${this.baseURL}/health-analytics/overview?user_id=${this.currentUser}`;
                
            const response = await fetch(url);
            if (!response.ok) throw new Error('获取概览统计失败');
            
            const stats = await response.json();
            this.updateOverviewStats(stats);
        } catch (error) {
            console.error('加载概览统计失败:', error);
            this.showError('加载概览统计失败');
        }
    }

    updateOverviewStats(stats) {
        document.getElementById('totalRecords').textContent = stats.total_records.toLocaleString();
        // 对于个人数据，用户总数始终为1
        document.getElementById('totalUsers').textContent = '1';
        document.getElementById('avgBMI').textContent = stats.avg_bmi ? stats.avg_bmi.toFixed(1) : '-';
        
        const avgBloodPressure = stats.avg_systolic && stats.avg_diastolic 
            ? `${Math.round(stats.avg_systolic)}/${Math.round(stats.avg_diastolic)}`
            : '-';
        document.getElementById('avgBloodPressure').textContent = avgBloodPressure;
        
        document.getElementById('avgBloodSugar').textContent = stats.avg_blood_sugar 
            ? stats.avg_blood_sugar.toFixed(1) + ' mmol/L'
            : '-';
    }

    async loadTrendData(metric) {
        try {
            // 始终使用当前用户ID
            const url = `${this.baseURL}/health-analytics/trends/${metric}?user_id=${this.currentUser}&period=${this.currentPeriod}`;
                
            const response = await fetch(url);
            if (!response.ok) throw new Error(`获取${metric}趋势数据失败`);
            
            const trendData = await response.json();
            this.updateTrendChart(metric, trendData);
        } catch (error) {
            console.error(`加载${metric}趋势数据失败:`, error);
        }
    }

    updateTrendChart(metric, trendData) {
        const chartId = this.getChartId(metric);
        const ctx = document.getElementById(chartId);
        if (!ctx) return;

        // 销毁现有图表
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
        }

        const labels = trendData.data.map(point => {
            const date = new Date(point.date);
            return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
        });

        const values = trendData.data.map(point => point.value);
        
        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: this.getMetricLabel(metric),
                    data: values,
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#00d4ff',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b8c3'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#b0b8c3'
                        }
                    }
                },
                elements: {
                    point: {
                        hoverBackgroundColor: '#ffffff'
                    }
                }
            }
        };

        this.charts[chartId] = new Chart(ctx, config);
    }

    async loadDistribution(metric) {
        try {
            // 始终使用当前用户ID
            const url = `${this.baseURL}/health-analytics/distribution/${metric}?user_id=${this.currentUser}`;
                
            const response = await fetch(url);
            if (!response.ok) throw new Error(`获取${metric}分布数据失败`);
            
            const distributionData = await response.json();
            this.updateDistributionChart(distributionData);
        } catch (error) {
            console.error(`加载${metric}分布数据失败:`, error);
        }
    }

    updateDistributionChart(distributionData) {
        const ctx = document.getElementById('distributionChart');
        if (!ctx) return;

        // 销毁现有图表
        if (this.charts.distributionChart) {
            this.charts.distributionChart.destroy();
        }

        const labels = distributionData.map(item => item.category);
        const values = distributionData.map(item => item.count);
        const colors = this.getDistributionColors(labels);

        const config = {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                cutout: '60%'
            }
        };

        this.charts.distributionChart = new Chart(ctx, config);
    }

    async loadUsersSummary() {
        try {
            // 直接获取当前用户的摘要信息
            const response = await fetch(`${this.baseURL}/health-analytics/users/summary?limit=1&user_id=${this.currentUser}`);
            if (!response.ok) throw new Error('获取用户摘要失败');
            
            const users = await response.json();
            this.updateUsersList(users);
        } catch (error) {
            console.error('加载用户摘要失败:', error);
            // 显示错误状态
            this.updateUsersList([]);
        }
    }

    updateUsersList(users) {
        const usersList = document.getElementById('usersList');
        const userCount = document.getElementById('userCount');
        
        // 更新标题为个人健康状况
        const usersHeader = document.querySelector('.users-container .chart-header h3');
        if (usersHeader) {
            usersHeader.textContent = '个人健康状况';
        }
        
        userCount.textContent = '当前用户';
        
        if (users.length === 0) {
            usersList.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-user-md"></i>
                    <p>暂无健康数据</p>
                    <small>请先添加健康记录以查看个人状况</small>
                </div>
            `;
            return;
        }

        const user = users[0]; // 当前用户数据
        const riskClass = this.getRiskClass(user.risk_level);
        const bmiText = user.bmi ? user.bmi.toFixed(1) : '-';
        const scoreText = user.health_score ? user.health_score.toFixed(0) : '-';
        const dateText = user.latest_record_date 
            ? new Date(user.latest_record_date).toLocaleDateString('zh-CN')
            : '-';

        // 根据BMI计算健康状态
        const bmiStatus = this.getBMIStatus(user.bmi);
        const healthAdvice = this.getHealthAdvice(user);

        usersList.innerHTML = `
            <div class="personal-health-card">
                <div class="health-header">
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="user-info">
                        <h4>${user.username}</h4>
                        <span class="last-update">最近更新: ${dateText}</span>
                    </div>
                    <div class="health-score">
                        <div class="score-circle ${this.getScoreClass(user.health_score)}">
                            <span class="score-number">${scoreText}</span>
                            <span class="score-label">健康评分</span>
                        </div>
                    </div>
                </div>
                
                <div class="health-metrics">
                    <div class="metric-item">
                        <div class="metric-icon">
                            <i class="fas fa-weight"></i>
                        </div>
                        <div class="metric-info">
                            <span class="metric-label">BMI指数</span>
                            <span class="metric-value">${bmiText}</span>
                            <span class="metric-status ${bmiStatus.class}">${bmiStatus.text}</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-icon">
                            <i class="fas fa-heartbeat"></i>
                        </div>
                        <div class="metric-info">
                            <span class="metric-label">健康风险</span>
                            <span class="metric-value risk-level ${riskClass}">${user.risk_level}</span>
                        </div>
                    </div>
                </div>
                
                <div class="health-advice">
                    <div class="advice-header">
                        <i class="fas fa-lightbulb"></i>
                        <span>健康建议</span>
                    </div>
                    <div class="advice-content">
                        ${healthAdvice}
                    </div>
                </div>
            </div>
        `;
    }

    getBMIStatus(bmi) {
        if (!bmi) return { text: '未知', class: 'unknown' };
        
        if (bmi < 18.5) {
            return { text: '偏瘦', class: 'underweight' };
        } else if (bmi < 24) {
            return { text: '正常', class: 'normal' };
        } else if (bmi < 28) {
            return { text: '超重', class: 'overweight' };
        } else {
            return { text: '肥胖', class: 'obese' };
        }
    }

    getScoreClass(score) {
        if (!score) return 'unknown';
        if (score >= 90) return 'excellent';
        if (score >= 80) return 'good';
        if (score >= 70) return 'fair';
        return 'poor';
    }

    getHealthAdvice(user) {
        const advices = [];
        
        if (user.bmi) {
            if (user.bmi < 18.5) {
                advices.push('建议增加营养摄入，适当增重');
            } else if (user.bmi >= 28) {
                advices.push('建议控制饮食，增加运动量');
            } else if (user.bmi >= 24) {
                advices.push('注意饮食平衡，保持适量运动');
            } else {
                advices.push('保持良好的生活习惯');
            }
        }
        
        if (user.risk_level === '高风险') {
            advices.push('建议定期体检，关注血压血糖');
        } else if (user.risk_level === '超重' || user.risk_level === '肥胖') {
            advices.push('建议制定减重计划');
        }
        
        if (user.health_score && user.health_score < 70) {
            advices.push('建议咨询医生，制定健康改善计划');
        }
        
        if (advices.length === 0) {
            advices.push('继续保持健康的生活方式');
        }
        
        return advices.map(advice => `<p><i class="fas fa-check-circle"></i> ${advice}</p>`).join('');
    }

    switchTrendMetric(button, metric) {
        // 更新按钮状态
        button.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // 加载新的趋势数据
        this.loadTrendData(metric);
    }

    switchDistribution(button, distribution) {
        // 更新按钮状态
        button.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // 加载新的分布数据
        this.loadDistribution(distribution);
    }

    getCurrentTrendMetric(chartType) {
        const container = chartType === 'weight' 
            ? document.querySelector('.chart-container:first-child')
            : document.querySelector('.chart-container:last-child');
        
        const activeBtn = container.querySelector('.chart-btn.active');
        return activeBtn ? activeBtn.dataset.metric : (chartType === 'weight' ? 'weight' : 'systolic');
    }

    getCurrentDistribution() {
        const activeBtn = document.querySelector('.distribution-container .chart-btn.active');
        return activeBtn ? activeBtn.dataset.distribution : 'bmi_category';
    }

    getChartId(metric) {
        if (metric === 'weight' || metric === 'bmi') {
            return 'weightChart';
        } else if (metric === 'systolic' || metric === 'diastolic') {
            return 'bloodPressureChart';
        }
        return 'weightChart';
    }

    getMetricLabel(metric) {
        const labels = {
            'weight': '体重 (kg)',
            'bmi': 'BMI',
            'systolic': '收缩压 (mmHg)',
            'diastolic': '舒张压 (mmHg)',
            'blood_sugar': '血糖 (mmol/L)',
            'cholesterol': '胆固醇 (mmol/L)'
        };
        return labels[metric] || metric;
    }

    getDistributionColors(labels) {
        const colorMap = {
            '正常': '#00ff7f',
            '偏瘦': '#87ceeb',
            '超重': '#ffa500',
            '肥胖': '#ff6347',
            '偏高': '#ffa500',
            '高血压': '#ff453a',
            '糖尿病': '#ff453a'
        };

        return labels.map(label => colorMap[label] || '#00d4ff');
    }

    getRiskClass(riskLevel) {
        if (riskLevel === '正常') return 'normal';
        if (riskLevel === '偏瘦' || riskLevel === '超重' || riskLevel === '偏高') return 'warning';
        return 'danger';
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showError(message) {
        const toast = document.getElementById('errorToast');
        const messageEl = document.getElementById('errorMessage');
        
        messageEl.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    }

    destroy() {
        // 清理定时器
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        // 销毁所有图表
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// 全局函数
function refreshAllData() {
    if (window.healthDashboard) {
        window.healthDashboard.refreshAllData();
    }
}

// 返回仪表盘功能
function goBackToDashboard() {
    // 尝试使用浏览器历史记录返回
    if (document.referrer && document.referrer.includes('dashboard.html')) {
        window.history.back();
    } else {
        // 直接跳转到仪表盘页面
        window.location.href = 'dashboard.html';
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.healthDashboard = new HealthDashboard();
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (window.healthDashboard) {
        window.healthDashboard.destroy();
    }
});