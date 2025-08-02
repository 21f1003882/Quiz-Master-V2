<template>
  <div>
    <!-- Registration Form -->
    <form @submit.prevent="handleRegister">
      <div v-if="registerMessage" class="alert alert-danger">{{ registerMessage }}</div>
      <div class="input-group mb-3"><span class="input-group-text">🙂</span><input type="text" class="form-control" placeholder="Username" v-model="regInfo.username" required></div>
      <div class="input-group mb-3"><span class="input-group-text">✉️</span><input type="email" class="form-control" placeholder="Email" v-model="regInfo.email" required></div>
      
      <div class="input-group mb-1"><span class="input-group-text">🔒</span><input type="password" class="form-control" placeholder="Password" v-model="regInfo.password" required></div>
      <small class="form-text text-muted d-block mb-3">
        Min 6 chars, 1 uppercase, 1 number, 1 special character.
      </small>

      <div class="input-group mb-3"><span class="input-group-text">🔒</span><input type="password" class="form-control" placeholder="Confirm Password" v-model="regInfo.confirm_password" required></div>
      <hr>
      <div class="input-group mb-3">
        <span class="input-group-text">❓</span>
        <select class="form-select secret-question-dropdown" v-model="regInfo.secret_question_id" required>
          <option :value="null" disabled>Please select a secret question</option>
          <option v-for="q in secretQuestions" :key="q.id" :value="q.id">{{ q.text }}</option>
        </select>
      </div>
      <div class="input-group mb-3"><span class="input-group-text">🤫</span><input type="text" class="form-control" placeholder="Secret Answer" v-model="regInfo.secret_answer" required></div>
      <button type="submit" class="btn btn-dark w-100" :disabled="loading">Create Account</button>
    </form>

    <!-- Success Modal -->
    <div class="modal fade" id="registrationSuccessModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Registration Successful!</h5>
            <button type="button" class="btn-close" @click="handleContinue"></button>
          </div>
          <div class="modal-body">
            <p>Please save your secret key. You will need it if you forget your password.</p>
            <div class="text-center p-3 secret-key-box">
              <strong style="font-family: monospace; font-size: 1.2rem;">{{ secretKey }}</strong>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-dark" @click="handleContinue">Continue to Dashboard</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import apiClient from '@/services/apiClient';
import { Modal } from 'bootstrap'; // Import Bootstrap's Modal JS

const auth = useAuthStore();

const secretKey = ref('');
const accessToken = ref(''); // To store the token for auto-login
const secretQuestions = ref([]);
const regInfo = reactive({
    username: '', email: '', password: '', confirm_password: '',
    secret_question_id: null, secret_answer: ''
});
const registerMessage = ref('');
const loading = ref(false);
let successModal = null; // To hold the modal instance

onMounted(async () => {
    // Initialize the modal instance
    const modalElement = document.getElementById('registrationSuccessModal');
    if (modalElement) {
      successModal = new Modal(modalElement, { keyboard: false, backdrop: 'static' });
    }
    
    try {
        const response = await apiClient.get('/auth/secret-questions');
        secretQuestions.value = response.data;
    } catch (error) {
        console.error("Could not fetch secret questions:", error);
    }
});

const validatePassword = (password) => {
  if (password.length < 6) return "Password must be at least 6 characters long.";
  if (!/[A-Z]/.test(password)) return "Password must contain at least one uppercase letter.";
  if (!/\d/.test(password)) return "Password must contain at least one number.";
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return "Password must contain at least one special character.";
  return null;
};

const handleRegister = async () => {
    loading.value = true;
    registerMessage.value = '';

    if (regInfo.password !== regInfo.confirm_password) {
        registerMessage.value = 'Passwords do not match.';
        loading.value = false;
        return;
    }
    const passwordError = validatePassword(regInfo.password);
    if (passwordError) {
        registerMessage.value = passwordError;
        loading.value = false;
        return;
    }

    try {
      const response = await auth.register(regInfo);
      secretKey.value = response.secret_key;
      accessToken.value = response.access_token; // Save the token
      successModal?.show(); // Show the success modal
    } catch (error) {
        registerMessage.value = error.response?.data?.message || 'Registration failed.';
    } finally {
        loading.value = false;
    }
};

const handleContinue = () => {
  successModal?.hide();
  // Use the token from registration to log the user in
  auth.setTokenAndRedirect(accessToken.value);
};

const reset = () => {
    registerMessage.value = '';
    Object.assign(regInfo, {
        username: '', email: '', password: '', confirm_password: '',
        secret_question_id: null, secret_answer: ''
    });
};

defineExpose({ reset });
</script>

<style scoped>
.secret-key-box {
  background-color: #e9ecef;
  border-radius: 0.375rem;
}

.secret-question-dropdown{
  font-size: 0.95em;
  color: rgb(103, 99, 99);
}
</style>