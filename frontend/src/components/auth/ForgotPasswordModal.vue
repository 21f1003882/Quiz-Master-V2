<template>
  <div class="modal fade" id="forgotPasswordModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Reset Password</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetModal"></button>
        </div>

        <!-- Step 1: Enter Email -->
        <div v-if="step === 1">
          <form @submit.prevent="handleGetQuestion">
            <div class="modal-body">
              <p>Please enter your email address to begin the password reset process.</p>
              <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
              <div class="input-group">
                <span class="input-group-text">✉️</span>
                <input type="email" class="form-control" placeholder="Your Email Address" v-model="email" required>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="resetModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                <span v-else>Continue</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Step 2: Verify Details -->
        <div v-if="step === 2">
          <form @submit.prevent="handleResetPassword">
            <div class="modal-body">
              <p>Hello, <strong>{{ username }}</strong>. Please answer the following to reset your password.</p>
              <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
              
              <div class="mb-3">
                <label class="form-label">Your Secret Question:</label>
                <p class="form-control-plaintext"><strong>{{ secret_question }}</strong></p>
              </div>

              <div class="input-group mb-3"><span class="input-group-text">🤫</span><input type="text" class="form-control" placeholder="Secret Answer" v-model="resetData.secret_answer" required></div>
              <div class="input-group mb-3"><span class="input-group-text">🔑</span><input type="text" class="form-control" placeholder="Secret Key (e.g., xxxx-xxxx-xxxx)" v-model="resetData.secret_key" required></div>
              <hr>
              <div class="input-group mb-1"><span class="input-group-text">🔒</span><input type="password" class="form-control" placeholder="New Password" v-model="resetData.new_password" required></div>
              <small class="form-text text-muted d-block mb-3">Min 6 chars, 1 uppercase, 1 number, 1 special character.</small>
              <div class="input-group mb-3"><span class="input-group-text">🔒</span><input type="password" class="form-control" placeholder="Confirm New Password" v-model="confirm_password" required></div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="resetModal">Start Over</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                <span v-else>Reset Password</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Step 3: Success -->
        <div v-if="step === 3">
            <div class="modal-body">
                <div class="alert alert-success">{{ successMessage }}</div>
                <p>You can now log in with your new password.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="resetModal">Close</button>
            </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useAuthStore } from '@/store/auth';

const auth = useAuthStore();

const step = ref(1);
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Step 1 state
const email = ref('');

// Step 2 state
const username = ref('');
const secret_question = ref('');
const confirm_password = ref('');
const resetData = reactive({
  email: '',
  secret_answer: '',
  secret_key: '',
  new_password: ''
});

const resetModal = () => {
  step.value = 1;
  loading.value = false;
  errorMessage.value = '';
  successMessage.value = '';
  email.value = '';
  username.value = '';
  secret_question.value = '';
  confirm_password.value = '';
  Object.assign(resetData, { email: '', secret_answer: '', secret_key: '', new_password: '' });
};

const handleGetQuestion = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    const response = await auth.getSecretQuestion(email.value);
    if (response.secret_question) {
      username.value = response.username;
      secret_question.value = response.secret_question;
      resetData.email = email.value; // Carry email over to the next step
      step.value = 2;
    } else {
      // Generic message even if user not found, to prevent email enumeration
      errorMessage.value = "If an account with that email exists, please check your details and try again. If the problem persists, contact support.";
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || "An error occurred.";
  } finally {
    loading.value = false;
  }
};

const handleResetPassword = async () => {
  loading.value = true;
  errorMessage.value = '';

  if (resetData.new_password !== confirm_password.value) {
    errorMessage.value = "New passwords do not match.";
    loading.value = false;
    return;
  }

  try {
    const response = await auth.resetPassword(resetData);
    successMessage.value = response.message;
    step.value = 3;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || "An error occurred.";
  } finally {
    loading.value = false;
  }
};
</script>