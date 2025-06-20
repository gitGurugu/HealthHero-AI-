// API 基础配置
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 认证管理类
class AuthManager {
    constructor() {
        this.token = localStorage.getItem('authToken');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }

    // 登录方法
    async login(username, password) {
        try {
            // 首先尝试真实的后端API登录
            const response = await fetch(`${API_BASE_URL}/users/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: username,
                    password: password
                })
            });

            if (response.ok) {
                const data = await response.json();
                // 保存认证信息
                this.token = data.access_token;
                this.user = {
                    id: data.user.id,
                    username: data.user.username,
                    email: data.user.email,
                    name: data.user.username
                };
                
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                
                return { success: true, data: data };
            } else {
                const errorData = await response.json();
                return { success: false, error: errorData.detail || '登录失败' };
            }
        } catch (error) {
            console.error('登录错误:', error);
            // 如果后端不可用，使用演示登录
            console.log('后端不可用，使用演示登录');
            return await this.demoLogin(username, password);
        }
    }

    // 演示登录功能（当后端不可用时）
    async demoLogin(username, password) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const user = DEMO_USERS.find(u => 
                    (u.username === username || u.email === username) && u.password === password
                );
                
                if (user) {
                    const token = 'demo_token_' + Date.now();
                    this.token = token;
                    this.user = {
                        id: user.id,
                        username: user.username,
                        email: user.email,
                        name: user.name
                    };
                    
                    localStorage.setItem('authToken', this.token);
                    localStorage.setItem('user', JSON.stringify(this.user));
                    
                    resolve({
                        success: true,
                        data: {
                            access_token: token,
                            user: this.user
                        }
                    });
                } else {
                    resolve({
                        success: false,
                        error: '用户名或密码错误'
                    });
                }
            }, 1000); // 模拟网络延迟
        });
    }

    // 注册方法
    async register(userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, data: data };
            } else {
                return { success: false, error: data.detail || '注册失败' };
            }
        } catch (error) {
            console.error('注册错误:', error);
            return { success: false, error: '网络连接错误' };
        }
    }

    // 登出方法
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        
        // 显示退出成功提示
        if (window.HealthHeroUtils) {
            HealthHeroUtils.showNotification('退出登录成功！', 'success', 1500);
        }
        
        // 延迟跳转，让用户看到成功消息
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 800);
    }

    // 检查是否已登录
    isAuthenticated() {
        return !!this.token;
    }

    // 获取认证头
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    // 获取用户信息
    getUser() {
        return this.user;
    }
}

// 创建全局认证管理器实例
const authManager = new AuthManager();

// 登录表单处理
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const loginBtn = document.querySelector('.login-btn');
    const btnText = document.querySelector('.btn-text');
    const loadingSpinner = document.querySelector('.loading-spinner');

    // 移除自动跳转逻辑，让用户可以自由访问登录页面
    // if (authManager.isAuthenticated()) {
    //     window.location.href = 'dashboard.html';
    //     return;
    // }

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;

            // 表单验证
            if (!username || !password) {
                showError('请填写用户名和密码');
                return;
            }

            // 显示加载状态
            showLoading(true);
            hideMessages();

            try {
                const result = await authManager.login(username, password);
                
                if (result.success) {
                    showSuccess('登录成功！正在跳转...');
                    
                    // 如果选择记住我，设置更长的过期时间
                    if (rememberMe) {
                        // 这里可以设置更长的token过期时间
                        console.log('用户选择记住登录状态');
                    }
                    
                    // 延迟跳转，让用户看到成功消息
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 1500);
                } else {
                    showError(result.error);
                }
            } catch (error) {
                console.error('登录处理错误:', error);
                showError('登录过程中发生错误，请重试');
            } finally {
                showLoading(false);
            }
        });
    }

    // 显示错误消息
    function showError(message) {
        if (errorMessage) {
            document.getElementById('errorText').textContent = message;
            errorMessage.style.display = 'flex';
            successMessage.style.display = 'none';
        }
    }

    // 显示成功消息
    function showSuccess(message) {
        if (successMessage) {
            document.getElementById('successText').textContent = message;
            successMessage.style.display = 'flex';
            errorMessage.style.display = 'none';
        }
    }

    // 隐藏所有消息
    function hideMessages() {
        if (errorMessage) errorMessage.style.display = 'none';
        if (successMessage) successMessage.style.display = 'none';
    }

    // 显示/隐藏加载状态
    function showLoading(show) {
        if (loginBtn && btnText && loadingSpinner) {
            if (show) {
                btnText.style.display = 'none';
                loadingSpinner.style.display = 'block';
                loginBtn.disabled = true;
            } else {
                btnText.style.display = 'block';
                loadingSpinner.style.display = 'none';
                loginBtn.disabled = false;
            }
        }
    }

    // 社交登录按钮事件
    const googleBtn = document.querySelector('.google-btn');
    const wechatBtn = document.querySelector('.wechat-btn');

    if (googleBtn) {
        googleBtn.addEventListener('click', function() {
            showError('Google 登录功能暂未开放，请使用用户名密码登录');
        });
    }

    if (wechatBtn) {
        wechatBtn.addEventListener('click', function() {
            showError('微信登录功能暂未开放，请使用用户名密码登录');
        });
    }
});

// 密码显示/隐藏切换
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleIcon.className = 'fas fa-eye';
    }
}

// 输入框焦点效果
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});

// 演示用户数据（实际项目中应该从后端获取）
const DEMO_USERS = [
    {
        username: 'demo',
        password: '123456',
        email: 'demo@healthhero.com',
        name: '演示用户'
    },
    {
        username: 'admin',
        password: 'admin123',
        email: 'admin@healthhero.com',
        name: '管理员'
    }
];

 