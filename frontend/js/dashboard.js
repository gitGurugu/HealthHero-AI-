// 仪表盘管理器
class DashboardManager {
    constructor() {
        this.currentUser = null;
        this.isInitialized = false;
        this.init();
    }

    async init() {
        if (this.isInitialized) {
            console.log('Dashboard already initialized');
            return;
        }

        try {
            console.log('Initializing dashboard...');
            this.setupEventListeners();
            this.loadUserInfo();
            this.setupNavigation();
            this.setCurrentDate();
            
            // 加载初始数据
            await this.loadDashboardData();
            
            this.isInitialized = true;
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
        }
    }

    setupEventListeners() {
        // 导航切换
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                // 如果是AI助手链接或数据大屏链接，允许正常跳转
                if (link.classList.contains('ai-assistant-link') || 
                    link.classList.contains('health-dashboard-link')) {
                    return; // 不阻止默认行为，允许正常跳转
                }
                
                e.preventDefault();
                const section = link.dataset.section;
                this.switchSection(section);
            });
        });

        // 表单提交事件
        this.setupFormHandlers();

        // 模态框事件
        this.setupModalHandlers();
    }

    setupFormHandlers() {
        // 健康数据表单
        const healthDataForm = document.getElementById('healthDataForm');
        if (healthDataForm) {
            healthDataForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitHealthData(e.target);
            });
        }

        // 运动记录表单
        const exerciseForm = document.getElementById('exerciseForm');
        if (exerciseForm) {
            exerciseForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitExerciseData(e.target);
            });
        }

        // 睡眠记录表单
        const sleepForm = document.getElementById('sleepForm');
        if (sleepForm) {
            sleepForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitSleepData(e.target);
            });
        }
    }

    setupModalHandlers() {
        // 点击模态框外部关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    loadUserInfo() {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        this.currentUser = user;
        
        // 添加调试信息
        console.log('Loading user info:', user);
        console.log('Current user ID:', user.id);
        
        // 验证用户信息
        if (!user.id) {
            console.error('用户ID缺失！用户可能未正确登录');
            this.showError('用户信息异常，请重新登录');
            return;
        }
        
        const userNameElement = document.getElementById('userName');
        if (userNameElement && user.username) {
            userNameElement.textContent = user.username;
        }
        
        // 显示当前用户ID（用于调试）
        const userIdElement = document.getElementById('userIdDebug');
        if (userIdElement) {
            userIdElement.textContent = `当前用户ID: ${user.id}`;
        }
    }

    setCurrentDate() {
        const currentDateElement = document.getElementById('currentDate');
        if (currentDateElement) {
            const now = new Date();
            const options = { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long'
            };
            currentDateElement.textContent = now.toLocaleDateString('zh-CN', options);
        }
    }

    switchSection(sectionName) {
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).parentElement.classList.add('active');

        // 切换内容区域
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');

        // 更新页面标题
        const titles = {
            'overview': '健康概览',
            'health-data': '健康数据管理',
            'exercise': '运动记录管理',
            'sleep': '睡眠记录管理'
        };
        document.querySelector('.page-title').textContent = titles[sectionName] || '健康仪表盘';

        // 加载对应数据
        this.loadSectionData(sectionName);
    }

    async loadSectionData(sectionName) {
        try {
            switch (sectionName) {
                case 'overview':
                    await this.loadOverviewData();
                    break;
                case 'health-data':
                    await this.loadHealthData();
                    break;
                case 'exercise':
                    await this.loadExerciseData();
                    break;
                case 'sleep':
                    await this.loadSleepData();
                    break;
            }
        } catch (error) {
            console.error(`Failed to load ${sectionName} data:`, error);
        }
    }

    async loadDashboardData() {
        this.showLoading(true);
        try {
            await Promise.all([
                this.loadOverviewData(),
                this.loadRecentRecords()
            ]);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('加载数据失败，请刷新页面重试');
        } finally {
            this.showLoading(false);
        }
    }

    async loadOverviewData() {
        if (!this.currentUser || !this.currentUser.id) {
            console.warn('No user ID available for loading overview data');
            return;
        }

        try {
            const userId = this.currentUser.id;
            
            // 并行加载各种数据的统计
            const [healthData, exerciseData, sleepData] = await Promise.all([
                this.apiCall(`/api/v1/health-data/user/${userId}?limit=100`),
                this.apiCall(`/api/v1/exercise-log/user/${userId}?limit=100`),
                this.apiCall(`/api/v1/sleep-record/user/${userId}?limit=100`)
            ]);

            // 更新统计数字
            this.updateStatCard('healthRecordsCount', healthData.length);
            this.updateStatCard('exerciseRecordsCount', exerciseData.length);
            this.updateStatCard('sleepRecordsCount', sleepData.length);

        } catch (error) {
            console.error('Failed to load overview data:', error);
        }
    }

    async loadRecentRecords() {
        if (!this.currentUser || !this.currentUser.id) {
            return;
        }

        try {
            const userId = this.currentUser.id;
            
            // 加载最近的记录
            const [healthData, exerciseData, sleepData] = await Promise.all([
                this.apiCall(`/api/v1/health-data/user/${userId}?limit=1`),
                this.apiCall(`/api/v1/exercise-log/user/${userId}?limit=1`),
                this.apiCall(`/api/v1/sleep-record/user/${userId}?limit=1`)
            ]);

            // 更新最近记录显示
            this.updateRecentHealthData(healthData[0]);
            this.updateRecentExercise(exerciseData[0]);
            this.updateRecentSleep(sleepData[0]);

        } catch (error) {
            console.error('Failed to load recent records:', error);
        }
    }

    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    updateRecentHealthData(data) {
        const container = document.getElementById('recentHealthData');
        if (!container) return;

        if (!data) {
            container.innerHTML = '<p class="no-data">暂无数据</p>';
            return;
        }

        const date = new Date(data.record_date).toLocaleDateString('zh-CN');
        container.innerHTML = `
            <div class="recent-item">
                <p><strong>记录日期:</strong> ${date}</p>
                ${data.weight ? `<p><strong>体重:</strong> ${data.weight} kg</p>` : ''}
                ${data.height ? `<p><strong>身高:</strong> ${data.height} cm</p>` : ''}
                ${data.systolic_pressure ? `<p><strong>血压:</strong> ${data.systolic_pressure}/${data.diastolic_pressure} mmHg</p>` : ''}
                ${data.blood_sugar ? `<p><strong>血糖:</strong> ${data.blood_sugar} mmol/L</p>` : ''}
            </div>
        `;
    }

    updateRecentExercise(data) {
        const container = document.getElementById('recentExercise');
        if (!container) return;

        if (!data) {
            container.innerHTML = '<p class="no-data">暂无数据</p>';
            return;
        }

        const date = new Date(data.log_date).toLocaleDateString('zh-CN');
        container.innerHTML = `
            <div class="recent-item">
                <p><strong>运动日期:</strong> ${date}</p>
                <p><strong>运动类型:</strong> ${data.exercise_type}</p>
                <p><strong>运动时长:</strong> ${data.duration_minutes} 分钟</p>
            </div>
        `;
    }

    updateRecentSleep(data) {
        const container = document.getElementById('recentSleep');
        if (!container) return;

        if (!data) {
            container.innerHTML = '<p class="no-data">暂无数据</p>';
            return;
        }

        const date = new Date(data.sleep_date).toLocaleDateString('zh-CN');
        const bedtime = new Date(data.bedtime).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        const wakeTime = new Date(data.wake_time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        
        container.innerHTML = `
            <div class="recent-item">
                <p><strong>睡眠日期:</strong> ${date}</p>
                <p><strong>就寝时间:</strong> ${bedtime}</p>
                <p><strong>起床时间:</strong> ${wakeTime}</p>
                ${data.sleep_quality ? `<p><strong>睡眠质量:</strong> ${data.sleep_quality}/10</p>` : ''}
                ${data.sleep_duration ? `<p><strong>睡眠时长:</strong> ${data.sleep_duration} 小时</p>` : ''}
            </div>
        `;
    }

    async loadHealthData() {
        if (!this.currentUser || !this.currentUser.id) return;

        try {
            const userId = this.currentUser.id;
            const data = await this.apiCall(`/api/v1/health-data/user/${userId}?limit=50`);
            
            this.renderHealthDataTable(data);
        } catch (error) {
            console.error('Failed to load health data:', error);
        }
    }

    renderHealthDataTable(data) {
        const tbody = document.querySelector('#healthDataTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="no-data">暂无数据</td></tr>';
            return;
        }

        data.forEach(record => {
            const row = document.createElement('tr');
            const date = new Date(record.record_date).toLocaleDateString('zh-CN');
            
            row.innerHTML = `
                <td>${date}</td>
                <td>${record.height || '-'}</td>
                <td>${record.weight || '-'}</td>
                <td>${record.systolic_pressure || '-'}</td>
                <td>${record.diastolic_pressure || '-'}</td>
                <td>${record.blood_sugar || '-'}</td>
                <td>${record.cholesterol || '-'}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="dashboard.deleteHealthRecord(${record.record_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadExerciseData() {
        if (!this.currentUser || !this.currentUser.id) return;

        try {
            const userId = this.currentUser.id;
            const data = await this.apiCall(`/api/v1/exercise-log/user/${userId}?limit=50`);
            
            this.renderExerciseTable(data);
        } catch (error) {
            console.error('Failed to load exercise data:', error);
        }
    }

    renderExerciseTable(data) {
        const tbody = document.querySelector('#exerciseTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="no-data">暂无数据</td></tr>';
            return;
        }

        data.forEach(record => {
            const row = document.createElement('tr');
            const date = new Date(record.log_date).toLocaleDateString('zh-CN');
            
            row.innerHTML = `
                <td>${date}</td>
                <td>${record.exercise_type}</td>
                <td>${record.duration_minutes}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="dashboard.deleteExerciseRecord(${record.log_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadSleepData() {
        if (!this.currentUser || !this.currentUser.id) return;

        try {
            const userId = this.currentUser.id;
            const data = await this.apiCall(`/api/v1/sleep-record/user/${userId}?limit=50`);
            
            this.renderSleepTable(data);
        } catch (error) {
            console.error('Failed to load sleep data:', error);
        }
    }

    renderSleepTable(data) {
        const tbody = document.querySelector('#sleepTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">暂无数据</td></tr>';
            return;
        }

        data.forEach(record => {
            const row = document.createElement('tr');
            const date = new Date(record.sleep_date).toLocaleDateString('zh-CN');
            
            // 处理时间格式 - 后端返回的是 time 对象 (如 "22:00:00")
            const formatTime = (timeStr) => {
                if (!timeStr) return '-';
                // 如果是时间字符串格式 "HH:MM:SS"
                if (typeof timeStr === 'string' && timeStr.includes(':')) {
                    const [hours, minutes] = timeStr.split(':');
                    return `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`;
                }
                // 如果是完整的日期时间
                try {
                    return new Date(timeStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
                } catch {
                    return timeStr;
                }
            };
            
            const bedtime = formatTime(record.bedtime);
            const wakeTime = formatTime(record.wake_time);
            
            row.innerHTML = `
                <td>${date}</td>
                <td>${bedtime}</td>
                <td>${wakeTime}</td>
                <td>${record.sleep_duration || '-'} 小时</td>
                <td>${record.sleep_quality || '-'}/10</td>
                <td>${record.deep_sleep_hours || '-'} 小时</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="dashboard.deleteSleepRecord(${record.sleep_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // API调用方法
    async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('authToken');
        const baseURL = 'http://localhost:8000'; // 根据你的后端地址调整
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        const response = await fetch(`${baseURL}${endpoint}`, {
            ...defaultOptions,
            ...options
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    // 表单提交方法
    async submitHealthData(form) {
        try {
            this.showLoading(true);
            
            const formData = new FormData(form);
            const data = {
                user_id: this.currentUser.id,
                record_date: formData.get('record_date'),
                height: formData.get('height') ? parseFloat(formData.get('height')) : null,
                weight: formData.get('weight') ? parseFloat(formData.get('weight')) : null,
                systolic_pressure: formData.get('systolic_pressure') ? parseInt(formData.get('systolic_pressure')) : null,
                diastolic_pressure: formData.get('diastolic_pressure') ? parseInt(formData.get('diastolic_pressure')) : null,
                blood_sugar: formData.get('blood_sugar') ? parseFloat(formData.get('blood_sugar')) : null,
                cholesterol: formData.get('cholesterol') ? parseFloat(formData.get('cholesterol')) : null
            };

            await this.apiCall('/api/v1/health-data/', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            this.closeModal('addHealthDataModal');
            form.reset();
            this.showSuccess('健康数据添加成功！');
            
            // 重新加载数据
            await this.loadHealthData();
            await this.loadOverviewData();
            
        } catch (error) {
            console.error('Failed to submit health data:', error);
            this.showError('添加健康数据失败，请重试');
        } finally {
            this.showLoading(false);
        }
    }

    async submitExerciseData(form) {
        try {
            this.showLoading(true);
            
            const formData = new FormData(form);
            const data = {
                user_id: this.currentUser.id,
                exercise_type: formData.get('exercise_type'),
                duration_minutes: parseInt(formData.get('duration_minutes')),
                log_date: formData.get('log_date')
            };

            await this.apiCall('/api/v1/exercise-log/', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            this.closeModal('addExerciseModal');
            form.reset();
            this.showSuccess('运动记录添加成功！');
            
            // 重新加载数据
            await this.loadExerciseData();
            await this.loadOverviewData();
            
        } catch (error) {
            console.error('Failed to submit exercise data:', error);
            this.showError('添加运动记录失败，请重试');
        } finally {
            this.showLoading(false);
        }
    }

    async submitSleepData(form) {
        try {
            this.showLoading(true);
            
            // 验证用户信息
            if (!this.currentUser || !this.currentUser.id) {
                console.error('用户信息缺失，无法提交数据');
                this.showError('用户信息异常，请重新登录');
                return;
            }
            
            console.log('提交睡眠数据，当前用户:', this.currentUser);
            console.log('使用的用户ID:', this.currentUser.id);
            
            const formData = new FormData(form);
            
            // 计算睡眠时长
            const bedtime = new Date(formData.get('bedtime'));
            const wakeTime = new Date(formData.get('wake_time'));
            const sleepDuration = (wakeTime - bedtime) / (1000 * 60 * 60); // 转换为小时
            
            // 格式化日期和时间
            const sleepDate = formData.get('sleep_date');
            const bedtimeISO = bedtime.toISOString();
            const wakeTimeISO = wakeTime.toISOString();
            
            const data = {
                user_id: this.currentUser.id,
                sleep_date: sleepDate,
                bedtime: bedtimeISO,
                wake_time: wakeTimeISO,
                sleep_duration: sleepDuration > 0 ? sleepDuration : null,
                sleep_quality: formData.get('sleep_quality') ? parseInt(formData.get('sleep_quality')) : null,
                deep_sleep_hours: formData.get('deep_sleep_hours') ? parseFloat(formData.get('deep_sleep_hours')) : null,
                notes: formData.get('notes') || null
            };

            console.log('提交的睡眠数据:', data);

            await this.apiCall('/api/v1/sleep-record/', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            this.closeModal('addSleepModal');
            form.reset();
            this.showSuccess('睡眠记录添加成功！');
            
            // 重新加载数据
            await this.loadSleepData();
            await this.loadOverviewData();
            
        } catch (error) {
            console.error('Failed to submit sleep data:', error);
            this.showError('添加睡眠记录失败，请重试');
        } finally {
            this.showLoading(false);
        }
    }

    // 删除记录方法
    async deleteHealthRecord(recordId) {
        if (!confirm('确定要删除这条健康记录吗？')) return;

        try {
            await this.apiCall(`/api/v1/health-data/${recordId}`, {
                method: 'DELETE'
            });

            this.showSuccess('健康记录删除成功！');
            await this.loadHealthData();
            await this.loadOverviewData();
        } catch (error) {
            console.error('Failed to delete health record:', error);
            this.showError('删除健康记录失败，请重试');
        }
    }

    async deleteExerciseRecord(recordId) {
        if (!confirm('确定要删除这条运动记录吗？')) return;

        try {
            await this.apiCall(`/api/v1/exercise-log/${recordId}`, {
                method: 'DELETE'
            });

            this.showSuccess('运动记录删除成功！');
            await this.loadExerciseData();
            await this.loadOverviewData();
        } catch (error) {
            console.error('Failed to delete exercise record:', error);
            this.showError('删除运动记录失败，请重试');
        }
    }

    async deleteSleepRecord(recordId) {
        if (!confirm('确定要删除这条睡眠记录吗？')) return;

        try {
            await this.apiCall(`/api/v1/sleep-record/${recordId}`, {
                method: 'DELETE'
            });

            this.showSuccess('睡眠记录删除成功！');
            await this.loadSleepData();
            await this.loadOverviewData();
        } catch (error) {
            console.error('Failed to delete sleep record:', error);
            this.showError('删除睡眠记录失败，请重试');
        }
    }

    // 模态框方法
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // 工具方法
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
            <button class="close-btn" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // 添加到页面
        document.body.appendChild(notification);

        // 自动移除
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// 全局函数
function showAddHealthDataModal() {
    dashboard.showModal('addHealthDataModal');
    
    // 设置默认日期为当前时间
    const now = new Date();
    const dateInput = document.getElementById('recordDate');
    if (dateInput) {
        dateInput.value = now.toISOString().slice(0, 16);
    }
}

function showAddExerciseModal() {
    dashboard.showModal('addExerciseModal');
    
    // 设置默认日期为当前时间
    const now = new Date();
    const dateInput = document.getElementById('exerciseDate');
    if (dateInput) {
        dateInput.value = now.toISOString().slice(0, 16);
    }
}

function showAddSleepModal() {
    dashboard.showModal('addSleepModal');
    
    // 设置默认日期为昨天
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    const dateInput = document.getElementById('sleepDate');
    if (dateInput) {
        dateInput.value = yesterday.toISOString().slice(0, 10);
    }
    
    // 设置默认就寝时间为昨晚22:00
    const bedtimeInput = document.getElementById('bedtime');
    if (bedtimeInput) {
        const bedtime = new Date(yesterday);
        bedtime.setHours(22, 0, 0, 0);
        bedtimeInput.value = bedtime.toISOString().slice(0, 16);
    }
    
    // 设置默认起床时间为今早7:00
    const wakeTimeInput = document.getElementById('wakeTime');
    if (wakeTimeInput) {
        const wakeTime = new Date();
        wakeTime.setHours(7, 0, 0, 0);
        wakeTimeInput.value = wakeTime.toISOString().slice(0, 16);
    }
}

function closeModal(modalId) {
    dashboard.closeModal(modalId);
}

function logout() {
    if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}

// 初始化仪表盘
let dashboard;
document.addEventListener('DOMContentLoaded', function() {
    // 检查认证状态
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // 初始化仪表盘
    dashboard = new DashboardManager();
});

// 全局错误处理
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    if (dashboard) {
        dashboard.showError('发生未知错误，请刷新页面重试');
    }
}); 