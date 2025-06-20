// AI助手管理器
class AIAssistantManager {
    constructor() {
        this.currentMode = 'basic'; // 'basic' 或 'health'
        this.currentUser = null;
        this.healthData = null;
        this.chatHistory = [];
        this.isTyping = false;
        
        this.init();
    }

    async init() {
        try {
            // 检查用户登录状态
            this.loadUserInfo();
            
            // 加载保存的健康数据
            this.loadHealthData();
            
            // 设置事件监听器
            this.setupEventListeners();
            
            // 加载快捷问题
            this.loadQuickQuestions();
            
            console.log('AI助手初始化完成');
        } catch (error) {
            console.error('AI助手初始化失败:', error);
        }
    }

    loadUserInfo() {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        this.currentUser = user;
        
        if (!user.id) {
            console.warn('用户未登录，跳转到登录页面');
            window.location.href = 'login.html';
            return;
        }
        
        // 更新用户信息显示
        const userNameElement = document.getElementById('userName');
        if (userNameElement && user.username) {
            userNameElement.textContent = user.username;
        }
    }

    setupEventListeners() {
        // 模式切换
        document.querySelectorAll('.mode-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });

        // 消息输入
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendMessage');
        
        messageInput.addEventListener('input', (e) => {
            this.handleInputChange(e.target.value);
        });
        
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // 健康数据面板
        document.getElementById('saveHealthData').addEventListener('click', () => {
            this.saveHealthData();
        });
        
        document.getElementById('skipHealthData').addEventListener('click', () => {
            this.skipHealthData();
        });

        // 聊天操作
        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });
        
        document.getElementById('exportChat').addEventListener('click', () => {
            this.exportChat();
        });

        // 快捷问题点击
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('question-item')) {
                const question = e.target.textContent;
                this.sendQuickQuestion(question);
            }
        });
    }

    switchMode(mode) {
        if (this.currentMode === mode) return;
        
        this.currentMode = mode;
        
        // 更新UI状态
        document.querySelectorAll('.mode-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        // 更新标题和描述
        const titles = {
            'basic': {
                title: 'AI健康助手 - 普通咨询',
                subtitle: '基础健康知识问答'
            },
            'health': {
                title: 'AI健康助手 - 个性化咨询',
                subtitle: '基于您的健康数据提供建议'
            }
        };
        
        document.getElementById('chatTitle').textContent = titles[mode].title;
        document.getElementById('chatSubtitle').textContent = titles[mode].subtitle;
        
        // 加载对应的快捷问题
        this.loadQuickQuestions();
        
        // 如果切换到健康模式且没有健康数据，显示数据输入面板
        if (mode === 'health' && !this.healthData) {
            this.showHealthDataPanel();
        } else {
            this.hideHealthDataPanel();
        }
        
        console.log(`切换到${mode}模式`);
    }

    loadQuickQuestions() {
        const questions = {
            'basic': [
                '什么是健康的生活方式？',
                '如何保持良好的睡眠质量？',
                '日常饮食需要注意什么？',
                '适合的运动有哪些？',
                '如何缓解工作压力？',
                '维生素的作用是什么？'
            ],
            'health': [
                '根据我的身体状况制定运动计划',
                '分析我的睡眠质量并给出建议',
                '为我推荐合适的饮食方案',
                '我的BMI指数正常吗？',
                '如何改善我的健康状况？',
                '制定个性化的健康目标'
            ]
        };
        
        const questionList = document.getElementById('quickQuestions');
        questionList.innerHTML = '';
        
        questions[this.currentMode].forEach(question => {
            const questionElement = document.createElement('div');
            questionElement.className = 'question-item';
            questionElement.textContent = question;
            questionList.appendChild(questionElement);
        });
    }

    handleInputChange(value) {
        const charCount = document.querySelector('.char-count');
        const sendButton = document.getElementById('sendMessage');
        
        charCount.textContent = `${value.length}/1000`;
        sendButton.disabled = value.trim().length === 0;
        
        // 自动调整输入框高度
        const textarea = document.getElementById('messageInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isTyping) return;
        
        // 清空输入框
        messageInput.value = '';
        this.handleInputChange('');
        
        // 添加用户消息到聊天记录
        this.addMessage('user', message);
        
        // 显示AI正在思考
        this.showTypingIndicator();
        
        try {
            let response;
            if (this.currentMode === 'basic') {
                response = await this.sendBasicChat(message);
            } else {
                response = await this.sendHealthChat(message);
            }
            
            // 流式响应已经在sendStreamingChat中处理了消息显示
            // 这里不需要再次添加消息
            
        } catch (error) {
            console.error('发送消息失败:', error);
            let errorMessage = '抱歉，我现在无法回答您的问题。';
            
            // 根据错误类型提供更具体的错误信息
            if (error.message.includes('500')) {
                errorMessage = '服务器内部错误，请稍后再试。如果问题持续存在，请联系管理员。';
            } else if (error.message.includes('timeout') || error.message.includes('Request timed out')) {
                errorMessage = 'AI服务响应超时，请稍后再试。您可以尝试提问更简单的问题。';
            } else if (error.message.includes('401')) {
                errorMessage = '身份验证失败，请重新登录。';
            } else if (error.message.includes('网络')) {
                errorMessage = '网络连接异常，请检查网络连接后重试。';
            }
            
            this.addMessage('ai', errorMessage);
            this.showNotification(errorMessage, 'error');
        } finally {
            this.hideTypingIndicator();
        }
    }

    async sendQuickQuestion(question) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = question;
        this.handleInputChange(question);
        await this.sendMessage();
    }

    async sendBasicChat(message) {
        return await this.sendStreamingChat('http://localhost:8000/api/v1/ai/chat/stream', {
            message: message
        });
    }

    async sendHealthChat(message) {
        if (!this.healthData) {
            return '请先完善您的健康信息，以便我为您提供更精准的建议。';
        }

        return await this.sendStreamingChat('http://localhost:8000/api/v1/ai/health/chat/stream', {
            message: message,
            user_data: this.healthData
        });
    }

    async sendStreamingChat(url, requestBody) {
        return new Promise((resolve, reject) => {
            let fullResponse = '';
            let currentMessageElement = null;
            
            // 创建AI消息元素
            const messagesContainer = document.getElementById('chatMessages');
            const messageElement = document.createElement('div');
            messageElement.className = 'message ai';
            
            const now = new Date();
            const timeString = now.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            messageElement.innerHTML = `
                <div class="ai-avatar-small">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-bubble">
                    <div class="message-content streaming"></div>
                    <div class="message-time">${timeString}</div>
                </div>
            `;
            
            // 移除欢迎消息
            const welcomeMessage = messagesContainer.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
            
            messagesContainer.appendChild(messageElement);
            currentMessageElement = messageElement.querySelector('.message-content');
            
            // 滚动到底部
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // 使用fetch进行流式请求
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(requestBody)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                const readStream = () => {
                    return reader.read().then(({ done, value }) => {
                        if (done) {
                            // 移除流式光标效果
                            currentMessageElement.classList.remove('streaming');
                            // 保存到聊天历史
                            this.chatHistory.push({
                                type: 'ai',
                                content: fullResponse,
                                timestamp: now.toISOString()
                            });
                            resolve(fullResponse);
                            return;
                        }
                        
                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    if (data.error) {
                                        throw new Error(data.error);
                                    }
                                    if (data.content && !data.done) {
                                        fullResponse += data.content;
                                        currentMessageElement.innerHTML = this.formatMessage(fullResponse);
                                        // 滚动到底部
                                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                    }
                                    if (data.done) {
                                        // 移除流式光标效果
                                        currentMessageElement.classList.remove('streaming');
                                        // 保存到聊天历史
                                        this.chatHistory.push({
                                            type: 'ai',
                                            content: fullResponse,
                                            timestamp: now.toISOString()
                                        });
                                        resolve(fullResponse);
                                        return;
                                    }
                                } catch (e) {
                                    console.error('解析流式数据失败:', e);
                                }
                            }
                        }
                        
                        return readStream();
                    });
                };
                
                return readStream();
            })
            .catch(error => {
                console.error('流式请求失败:', error);
                if (currentMessageElement) {
                    currentMessageElement.classList.remove('streaming');
                    currentMessageElement.innerHTML = '抱歉，AI服务暂时不可用，请稍后再试。';
                }
                reject(error);
            });
        });
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        if (type === 'user') {
            messageElement.innerHTML = `
                <div class="user-avatar-small">
                    <i class="fas fa-user"></i>
                </div>
                <div class="message-bubble">
                    ${this.formatMessage(content)}
                    <div class="message-time">${timeString}</div>
                </div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="ai-avatar-small">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-bubble">
                    ${this.formatMessage(content)}
                    <div class="message-time">${timeString}</div>
                </div>
            `;
        }
        
        // 移除欢迎消息
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        messagesContainer.appendChild(messageElement);
        
        // 滚动到底部
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // 保存到聊天历史
        this.chatHistory.push({
            type: type,
            content: content,
            timestamp: now.toISOString()
        });
    }

    formatMessage(content) {
        // 简单的文本格式化
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    showTypingIndicator() {
        this.isTyping = true;
        document.getElementById('typingIndicator').style.display = 'flex';
        document.getElementById('sendMessage').disabled = true;
    }

    hideTypingIndicator() {
        this.isTyping = false;
        document.getElementById('typingIndicator').style.display = 'none';
        
        const messageInput = document.getElementById('messageInput');
        document.getElementById('sendMessage').disabled = messageInput.value.trim().length === 0;
    }

    showHealthDataPanel() {
        document.getElementById('healthDataPanel').style.display = 'block';
        
        // 如果有保存的健康数据，填充表单
        const savedData = localStorage.getItem('healthData');
        if (savedData) {
            const data = JSON.parse(savedData);
            this.fillHealthForm(data);
        }
    }

    hideHealthDataPanel() {
        document.getElementById('healthDataPanel').style.display = 'none';
    }

    fillHealthForm(data) {
        document.getElementById('userAge').value = data.age || '';
        document.getElementById('userHeight').value = data.height || '';
        document.getElementById('userWeight').value = data.weight || '';
        document.getElementById('avgSleep').value = data.avg_sleep_hours || '';
        document.getElementById('bedtime').value = data.sleep_schedule?.bedtime || '';
        document.getElementById('wakeTime').value = data.sleep_schedule?.wake_time || '';
        document.getElementById('exerciseContraindications').value = data.exercise_contraindications || '';
    }

    saveHealthData() {
        const healthData = {
            age: parseInt(document.getElementById('userAge').value) || null,
            height: parseFloat(document.getElementById('userHeight').value) || null,
            weight: parseFloat(document.getElementById('userWeight').value) || null,
            avg_sleep_hours: parseFloat(document.getElementById('avgSleep').value) || null,
            sleep_schedule: {
                bedtime: document.getElementById('bedtime').value || null,
                wake_time: document.getElementById('wakeTime').value || null
            },
            exercise_contraindications: document.getElementById('exerciseContraindications').value || null,
            diet_records: [], // 可以后续从用户的饮食记录中获取
            sleep_issues: [] // 可以后续从用户的睡眠记录中获取
        };
        
        this.healthData = healthData;
        localStorage.setItem('healthData', JSON.stringify(healthData));
        
        this.hideHealthDataPanel();
        this.showNotification('健康信息保存成功！', 'success');
        
        console.log('健康数据已保存:', healthData);
    }

    skipHealthData() {
        this.hideHealthDataPanel();
        this.showNotification('您可以随时在个性化咨询模式下完善健康信息', 'info');
    }

    clearChat() {
        if (confirm('确定要清空所有对话记录吗？')) {
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <div class="ai-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <h4>👋 您好！我是您的AI健康助手</h4>
                        <p>我可以为您提供：</p>
                        <ul>
                            <li>🔍 健康知识问答</li>
                            <li>💡 个性化健康建议</li>
                            <li>🏃‍♂️ 运动计划制定</li>
                            <li>🥗 饮食营养指导</li>
                            <li>😴 睡眠质量改善</li>
                        </ul>
                        <p>请选择咨询模式开始对话吧！</p>
                    </div>
                </div>
            `;
            
            this.chatHistory = [];
            this.showNotification('对话记录已清空', 'success');
        }
    }

    exportChat() {
        if (this.chatHistory.length === 0) {
            this.showNotification('没有对话记录可以导出', 'warning');
            return;
        }
        
        const chatText = this.chatHistory.map(msg => {
            const time = new Date(msg.timestamp).toLocaleString('zh-CN');
            const sender = msg.type === 'user' ? '用户' : 'AI助手';
            return `[${time}] ${sender}: ${msg.content}`;
        }).join('\n\n');
        
        const blob = new Blob([chatText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AI健康助手对话记录_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('对话记录已导出', 'success');
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1001;
            display: flex;
            align-items: center;
            gap: 8px;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    loadHealthData() {
        const savedData = localStorage.getItem('healthData');
        if (savedData) {
            try {
                this.healthData = JSON.parse(savedData);
                console.log('已加载保存的健康数据:', this.healthData);
            } catch (error) {
                console.error('解析健康数据失败:', error);
                localStorage.removeItem('healthData');
            }
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 添加通知动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // 初始化AI助手
    window.aiAssistant = new AIAssistantManager();
}); 