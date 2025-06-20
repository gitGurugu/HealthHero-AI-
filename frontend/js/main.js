// 主要应用程序逻辑
class HealthHeroApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        // 移除checkAuthStatus调用，避免任何可能的跳转
        // this.checkAuthStatus();
        this.setupFormValidation();
    }

    // 设置事件监听器
    setupEventListeners() {
        // 页面加载完成后的初始化
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeComponents();
        });

        // 处理页面可见性变化 - 暂时禁用以避免重复检查
        // document.addEventListener('visibilitychange', () => {
        //     if (!document.hidden) {
        //         this.checkAuthStatus();
        //     }
        // });

        // 处理网络状态变化
        window.addEventListener('online', () => {
            this.showNetworkStatus('网络连接已恢复', 'success');
        });

        window.addEventListener('offline', () => {
            this.showNetworkStatus('网络连接已断开', 'error');
        });
    }

    // checkAuthStatus方法已完全移除，不再进行任何认证检查或跳转



    // 初始化组件
    initializeComponents() {
        this.initializeAnimations();
        this.initializeFormEffects();
    }

    // 初始化动画
    initializeAnimations() {
        // 添加页面加载动画
        const elements = document.querySelectorAll('.feature-item, .login-container');
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.1}s`;
        });
    }

    // 初始化表单效果
    initializeFormEffects() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"]');
        
        inputs.forEach(input => {
            // 添加浮动标签效果
            this.setupFloatingLabel(input);
            
            // 添加输入验证
            input.addEventListener('blur', () => {
                this.validateInput(input);
            });
            
            // 添加实时验证
            input.addEventListener('input', () => {
                this.clearInputError(input);
            });
        });
    }

    // 设置浮动标签
    setupFloatingLabel(input) {
        const wrapper = input.closest('.input-wrapper');
        if (!wrapper) return;

        input.addEventListener('focus', () => {
            wrapper.classList.add('focused');
        });

        input.addEventListener('blur', () => {
            if (!input.value) {
                wrapper.classList.remove('focused');
            }
        });

        // 如果输入框已有值，保持焦点状态
        if (input.value) {
            wrapper.classList.add('focused');
        }
    }

    // 设置表单验证
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    // 验证表单
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    // 验证单个输入
    validateInput(input) {
        const value = input.value.trim();
        const type = input.type;
        let isValid = true;
        let errorMessage = '';

        // 必填验证
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = '此字段为必填项';
        }
        // 邮箱验证
        else if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            errorMessage = '请输入有效的邮箱地址';
        }
        // 密码验证
        else if (type === 'password' && value && value.length < 6) {
            isValid = false;
            errorMessage = '密码长度至少为6位';
        }

        if (!isValid) {
            this.showInputError(input, errorMessage);
        } else {
            this.clearInputError(input);
        }

        return isValid;
    }

    // 显示输入错误
    showInputError(input, message) {
        const wrapper = input.closest('.form-group');
        if (!wrapper) return;

        // 移除现有错误
        this.clearInputError(input);

        // 添加错误样式
        input.classList.add('error');
        
        // 创建错误消息
        const errorElement = document.createElement('div');
        errorElement.className = 'input-error';
        errorElement.textContent = message;
        
        wrapper.appendChild(errorElement);
    }

    // 清除输入错误
    clearInputError(input) {
        const wrapper = input.closest('.form-group');
        if (!wrapper) return;

        input.classList.remove('error');
        
        const errorElement = wrapper.querySelector('.input-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    // 邮箱验证
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // 显示网络状态
    showNetworkStatus(message, type) {
        const notification = document.createElement('div');
        notification.className = `network-notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-wifi' : 'fa-exclamation-triangle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // 自动移除通知
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// 创建应用实例
const app = new HealthHeroApp();

// 全局工具函数
window.HealthHeroUtils = {
    // 显示通知
    showNotification: (message, type = 'info', duration = 3000) => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                           type === 'error' ? 'fa-exclamation-circle' : 
                           type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
            <button class="close-btn" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // 自动移除
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.classList.add('fade-out');
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }, 300);
                }
            }, duration);
        }
    },

    // 显示确认对话框
    confirm: (message, callback) => {
        const confirmModal = document.createElement('div');
        confirmModal.className = 'confirm-modal';
        confirmModal.innerHTML = `
            <div class="confirm-overlay"></div>
            <div class="confirm-dialog">
                <div class="confirm-header">
                    <i class="fas fa-question-circle"></i>
                    <h3>确认操作</h3>
                </div>
                <div class="confirm-body">
                    <p>${message}</p>
                </div>
                <div class="confirm-footer">
                    <button class="btn btn-secondary cancel-btn">取消</button>
                    <button class="btn btn-primary confirm-btn">确定</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(confirmModal);
        
        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .confirm-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .confirm-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            
            .confirm-dialog {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                max-width: 400px;
                width: 90%;
                animation: confirmSlideIn 0.3s ease-out;
            }
            
            .confirm-header {
                padding: 24px 24px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .confirm-header i {
                color: #f59e0b;
                font-size: 24px;
            }
            
            .confirm-header h3 {
                margin: 0;
                color: #1f2937;
                font-size: 18px;
                font-weight: 600;
            }
            
            .confirm-body {
                padding: 16px 24px;
            }
            
            .confirm-body p {
                margin: 0;
                color: #6b7280;
                font-size: 16px;
                line-height: 1.5;
            }
            
            .confirm-footer {
                padding: 16px 24px 24px;
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            .confirm-footer .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .confirm-footer .btn-secondary {
                background: #f3f4f6;
                color: #6b7280;
            }
            
            .confirm-footer .btn-secondary:hover {
                background: #e5e7eb;
            }
            
            .confirm-footer .btn-primary {
                background: #3b82f6;
                color: white;
            }
            
            .confirm-footer .btn-primary:hover {
                background: #2563eb;
            }
            
            @keyframes confirmSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px) scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
        `;
        document.head.appendChild(style);
        
        // 事件处理
        const cancelBtn = confirmModal.querySelector('.cancel-btn');
        const confirmBtn = confirmModal.querySelector('.confirm-btn');
        const overlay = confirmModal.querySelector('.confirm-overlay');
        
        const cleanup = () => {
            document.body.removeChild(confirmModal);
            document.head.removeChild(style);
        };
        
        cancelBtn.addEventListener('click', () => {
            cleanup();
            if (callback) callback(false);
        });
        
        confirmBtn.addEventListener('click', () => {
            cleanup();
            if (callback) callback(true);
        });
        
        overlay.addEventListener('click', () => {
            cleanup();
            if (callback) callback(false);
        });
        
        // ESC键取消
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                cleanup();
                if (callback) callback(false);
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }
};
