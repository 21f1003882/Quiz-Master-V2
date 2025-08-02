<template>
  <div>
    <div class="container login-page-container">
      <div class="row justify-content-center align-items-center min-vh-100 m-0 login-container-row">
        <div class="col-11 col-sm-10 col-md-8 col-lg-6 col-xl-5">
          <div class="card login-card shadow-lg">
            <div class="card-body p-4 p-md-5">

              <div class="text-center mb-4">
                <img class="logoImg" src="/src/assets/images/quiz-logo.jpg" alt="QuizApp">
                <h4 class="loginwelcometitle">Welcome to QuizApp</h4>
              </div>

              <!-- Tab Navigation -->
              <ul class="nav nav-pills nav-fill mb-4 sign-in-option" id="pills-tab" role="tablist">
                <li class="nav-item" role="presentation">
                  <button class="nav-link active" id="pills-login-tab" data-bs-toggle="pill" data-bs-target="#pills-login" type="button" role="tab" aria-selected="true">Sign In</button>
                </li>
                <li class="nav-item register-option" role="presentation">
                  <button class="nav-link" id="pills-register-tab" data-bs-toggle="pill" data-bs-target="#pills-register" type="button" role="tab" aria-selected="false" @click="onRegisterTabClick">Create Account</button>
                </li>
              </ul>

              <!-- Tab Content -->
              <div class="tab-content" id="pills-tabContent">
                <!-- Login Pane -->
                <div class="tab-pane fade show active" id="pills-login" role="tabpanel">
                  <LoginForm />
                </div>

                <!-- Register Pane -->
                <div class="tab-pane fade" id="pills-register" role="tabpanel">
                  <RegisterForm ref="registerForm" @switchToLogin="switchToLoginTab" />
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  
    <ForgotPasswordModal />
  </div>
</template>
  
<script setup>
import { ref } from 'vue';
import { Tab } from 'bootstrap';
import LoginForm from '../components/auth/LoginForm.vue';
import RegisterForm from '../components/auth/RegisterForm.vue';
import ForgotPasswordModal from '../components/auth/ForgotPasswordModal.vue';

const registerForm = ref(null);

// When the user clicks the "Create Account" tab, reset the form inside the child component.
const onRegisterTabClick = () => {
  if (registerForm.value) {
    registerForm.value.reset();
  }
};

// When the registration is successful, the child component emits an event to switch tabs.
const switchToLoginTab = () => {
  const loginTab = document.querySelector('#pills-login-tab');
  if (loginTab) {
    const tab = new Tab(loginTab);
    tab.show();
  }
};
</script>
  
<style scoped>
  .login-card {
    border: none;
    border-radius: 0.75rem;
  }
  .logoImg {
    width: 50px;
    height: 50px;
    border-radius: 30%;
    transform: rotate(-40deg);
    margin-bottom: 1rem;
  }
  .nav-pills .nav-link {
    color: black;

  }
  .nav-pills .nav-link.active {
    background-color: #343a40;
    color: white;
  }
</style>
