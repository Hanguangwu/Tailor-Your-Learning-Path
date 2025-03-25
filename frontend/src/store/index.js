import { createStore } from 'vuex'
import auth from './modules/auth'
import courses from './modules/courses'
import profile from './modules/profile'
export default createStore({
  modules: {
    auth,
    courses,
    profile
  }
})