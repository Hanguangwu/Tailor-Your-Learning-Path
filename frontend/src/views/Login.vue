<template>
  <div class="login-container">
    <div class="login-card">
      <h2>欢迎回来</h2>
      <div class="form-group">
        <input
          v-model="loginForm.username"
          type="text"
          placeholder="用户名/邮箱"
          class="form-input"
        />
      </div>
      <div class="form-group">
        <input
          v-model="loginForm.password"
          type="password"
          placeholder="密码"
          class="form-input"
        />
      </div>
      <div class="form-options">
        <label class="remember-me">
          <input type="checkbox" v-model="loginForm.remember" />
          <span>记住我</span>
        </label>
        <a href="#" class="forgot-password">忘记密码？</a>
      </div>
      <button @click="handleLogin" class="login-btn">登录</button>
      <div class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
        remember: false
      }
    }
  },
  methods: {
    async handleLogin() {
      try {
        // 使用 Vuex action 进行登录
        const response = await this.$store.dispatch('auth/login', {
          username: this.loginForm.username,  // 后端接收 username 作为邮箱
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
    }
  }
}
</script>

<style scoped>
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
</style>