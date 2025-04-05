<template>
  <div class="login-container">
    <div class="login-card">
      <h2>欢迎回来</h2>
      <div class="form-group">
        <input v-model="loginForm.username" type="text" placeholder="用户名/邮箱" class="form-input" />
      </div>
      <div class="form-group">
        <input v-model="loginForm.password" type="password" placeholder="密码" class="form-input" />
      </div>
      <div class="form-options">
        <label class="remember-me">
          <input type="checkbox" v-model="loginForm.remember" />
          <span>记住我</span>
        </label>
        <a href="#" class="forgot-password" @click.prevent="showForgotPassword">忘记密码？</a>
      </div>
      <button @click="handleLogin" class="login-btn">登录</button>
      <div class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
    <!-- 修改忘记密码对话框 -->
    <el-dialog v-model="forgotPasswordVisible" title="忘记密码" width="30%" class="forgot-password-dialog">
      <!-- 步骤1: 输入邮箱 -->
      <div v-if="resetStep === 1">
        <el-form :model="forgotPasswordForm" :rules="forgotPasswordRules" ref="forgotPasswordFormRef">
          <el-form-item prop="email" label="邮箱">
            <el-input v-model="forgotPasswordForm.email" placeholder="请输入注册邮箱"></el-input>
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="forgotPasswordVisible = false">取消</el-button>
          <el-button type="primary" @click="sendResetCode" :loading="sending" :disabled="isTime">
            {{ isTime ? `请于${currentTime}s后重试` : '发送验证码' }}
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 验证验证码 -->
      <div v-if="resetStep === 2">
        <el-form :model="verifyCodeForm" :rules="verifyCodeRules" ref="verifyCodeFormRef">
          <el-form-item prop="code" label="验证码">
            <div class="code-container">
              <el-input v-model="verifyCodeForm.code" placeholder="请输入6位验证码"></el-input>
              <el-button type="primary" @click="sendResetCode" :loading="sending" :disabled="isTime" class="resend-btn">
                {{ isTime ? `${currentTime}s` : '重新发送' }}
              </el-button>
            </div>
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="backToEmailStep">返回</el-button>
          <el-button type="primary" @click="verifyCode" :loading="verifying">
            验证
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 设置新密码 -->
      <div v-if="resetStep === 3">
        <el-form :model="resetPasswordForm" :rules="resetPasswordRules" ref="resetPasswordFormRef">
          <el-form-item prop="newPassword" label="新密码">
            <el-input v-model="resetPasswordForm.newPassword" type="password" placeholder="请输入新密码"></el-input>
          </el-form-item>
          <el-form-item prop="confirmPassword" label="确认密码">
            <el-input v-model="resetPasswordForm.confirmPassword" type="password" placeholder="请再次输入新密码"></el-input>
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="backToVerifyStep">返回</el-button>
          <el-button type="primary" @click="confirmResetPassword" :loading="resetting">
            重置密码
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from '@/axios'

export default {
  name: 'Login',
  data() {
    // 密码确认验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.resetPasswordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      loginForm: {
        username: '',
        password: '',
        remember: false
      },
      // 修改忘记密码相关数据
      forgotPasswordVisible: false,
      resetStep: 1, // 重置密码步骤：1-输入邮箱, 2-验证验证码, 3-设置新密码
      sending: false,
      verifying: false,
      resetting: false,
      isTime: false,
      currentTime: 60,
      forgotPasswordForm: {
        email: ''
      },
      verifyCodeForm: {
        code: ''
      },
      resetPasswordForm: {
        newPassword: '',
        confirmPassword: ''
      },
      forgotPasswordRules: {
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ]
      },
      verifyCodeRules: {
        code: [
          { required: true, message: '请输入验证码', trigger: 'blur' },
          { len: 6, message: '验证码长度应为6位', trigger: 'blur' }
        ]
      },
      resetPasswordRules: {
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await this.$store.dispatch('auth/login', {
          username: this.loginForm.username,
          password: this.loginForm.password
        })

        if (this.loginForm.remember) {
          localStorage.setItem('token', response.access_token)
          localStorage.setItem('user', JSON.stringify(response.user))
        }

        this.$router.push('/')
      } catch (error) {
        this.$message.error(error.response?.data?.detail || '登录失败，请稍后重试')
      }
    },

    // 修改忘记密码相关方法
    showForgotPassword() {
      this.forgotPasswordVisible = true
      this.resetStep = 1
      this.isTime = false
      this.currentTime = 60
      this.forgotPasswordForm.email = ''
      this.verifyCodeForm.code = ''
      this.resetPasswordForm.newPassword = ''
      this.resetPasswordForm.confirmPassword = ''
    },

    // 返回邮箱输入步骤
    backToEmailStep() {
      this.resetStep = 1
    },

    // 返回验证码验证步骤
    backToVerifyStep() {
      this.resetStep = 2
    },

    async sendResetCode() {
      try {
        if (this.resetStep === 1) {
          await this.$refs.forgotPasswordFormRef.validate()
        }
        
        this.sending = true
        
        // 设置倒计时
        this.isTime = true
        this.currentTime = 60
        const interval = setInterval(() => {
          this.currentTime--
          if (this.currentTime === 0) {
            clearInterval(interval)
            this.isTime = false
          }
        }, 1000)
        
        // 发送验证码请求
        const response = await axios.post('/api/auth/send-code', {
          email: this.forgotPasswordForm.email,
          type: 'reset_password'
        })
        
        // 如果是第一步，进入第二步
        if (this.resetStep === 1) {
          this.resetStep = 2
        }
        
        this.$message.success('验证码已发送到您的邮箱')
      } catch (error) {
        console.error('发送验证码错误:', error)
        this.$message.error(error.response?.data?.detail || '发送验证码失败')
      } finally {
        this.sending = false
      }
    },

    // 验证验证码
    async verifyCode() {
      try {
        await this.$refs.verifyCodeFormRef.validate()
        this.verifying = true
        
        // 发送验证码验证请求
        const response = await axios.post('/api/auth/verify-code', {
          email: this.forgotPasswordForm.email,
          code: this.verifyCodeForm.code,
          type: 'reset_password'
        })
        
        // 验证成功，进入设置新密码步骤
        this.resetStep = 3
        this.$message.success('验证码验证成功')
      } catch (error) {
        console.error('验证码验证错误:', error)
        this.$message.error(error.response?.data?.detail || '验证码验证失败')
      } finally {
        this.verifying = false
      }
    },

    // 确认重置密码
    async confirmResetPassword() {
      try {
        await this.$refs.resetPasswordFormRef.validate()
        this.resetting = true
        
        // 发送重置密码请求
        const response = await axios.post('/api/auth/reset-password', {
          email: this.forgotPasswordForm.email,
          code: this.verifyCodeForm.code,
          new_password: this.resetPasswordForm.newPassword
        })
        
        this.$message.success('密码重置成功')
        this.forgotPasswordVisible = false
        
        // 清空表单
        this.forgotPasswordForm.email = ''
        this.verifyCodeForm.code = ''
        this.resetPasswordForm.newPassword = ''
        this.resetPasswordForm.confirmPassword = ''
      } catch (error) {
        console.error('重置密码错误:', error)
        this.$message.error(error.response?.data?.detail || '重置密码失败')
      } finally {
        this.resetting = false
      }
    }
  }
}
</script>

<style scoped>
/* 样式保持不变 */
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('../assets/wallhaven-login.jpg') no-repeat center center;
  background-size: cover;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  backdrop-filter: blur(10px);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #409EFF;
  outline: none;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
}

.forgot-password {
  color: #409EFF;
  text-decoration: none;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background: #66b1ff;
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.register-link a {
  color: #409EFF;
  text-decoration: none;
  margin-left: 0.5rem;
}

/* 修改忘记密码对话框样式 */
.forgot-password-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 添加验证码输入框样式 */
.code-container {
  display: flex;
  gap: 10px;
}

.resend-btn {
  white-space: nowrap;
  min-width: 100px;
}
</style>