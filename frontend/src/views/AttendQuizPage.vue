<template>
    <div class="container">
      <div v-if="loading" class="text-center my-5"><div class="spinner-border" style="width: 3rem; height: 3rem;"></div></div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
  
      <!-- Quiz Interface -->
      <div v-else-if="!quizResult" class="card shadow-sm">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h4 class="mb-0">{{ quiz.title }}</h4>
          <div id="timer" class="badge bg-light p-2 fs-6">{{ formattedTime }}</div>
        </div>
        <div class="card-body">
          <div class="progress mb-4" style="height: 10px;">
            <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
          </div>
  
          <div v-if="currentQuestion">
            <p class="lead">Question {{ currentQuestionIndex + 1 }} of {{ quiz.questions.length }}</p>
            <h5 class="mb-4" style="white-space: pre-wrap;">{{ currentQuestion.text }}</h5>
            <div class="options-list">
              <div v-for="option in currentQuestion.options" :key="option.id" class="form-check mb-3">
                <input class="form-check-input" type="radio" :name="'q_'+currentQuestion.id" :id="'opt_'+option.id" :value="option.id" v-model="userAnswers[currentQuestion.id]" :disabled="questionStatus[currentQuestion.id]?.checked">
                <label class="form-check-label" :for="'opt_'+option.id" :class="getOptionClass(option.id)">{{ option.text }}</label>
              </div>
            </div>
          </div>
  
          <!-- Navigation -->
          <div class="d-flex justify-content-between mt-4">
            <button class="btn btn-secondary" @click="prevQuestion" :disabled="currentQuestionIndex === 0">Previous</button>
            <div>
              <button v-if="!questionStatus[currentQuestion.id]?.checked" class="btn btn-info me-2" @click="handleCheckAnswer" :disabled="!userAnswers[currentQuestion.id] || checkingAnswer">
                <span v-if="checkingAnswer" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                <span v-else>Check Answer</span>
              </button>
              <button v-if="questionStatus[currentQuestion.id]?.checked && currentQuestionIndex < quiz.questions.length - 1" class="btn btn-primary" @click="nextQuestion">Next &raquo;</button>
              <button v-if="questionStatus[currentQuestion.id]?.checked && currentQuestionIndex === quiz.questions.length - 1" class="btn btn-success" @click="confirmSubmit">Submit Quiz</button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Quiz Results Display -->
      <div v-else class="card shadow-sm">
        <div class="card-header"><h4 class="mb-0">Quiz Results: {{ quiz.title }}</h4></div>
        <div class="card-body text-center">
          <h2 class="display-4">You Scored</h2>
          <p class="display-1 fw-bold">{{ quizResult.score }} / {{ quizResult.total_questions }}</p>
          <p class="h3">({{ quizResult.percentage }}%)</p>
          <router-link :to="{ name: 'UserDashboard' }" class="btn btn-primary mt-4">Back to Dashboard</router-link>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import userService from '@/services/userService';
  
  const props = defineProps({ attemptId: { type: String, required: true } });
  const router = useRouter();
  
  const loading = ref(true);
  const error = ref('');
  const quiz = ref({ title: '', questions: [] });
  const userAnswers = reactive({});
  const questionStatus = reactive({});
  const quizResult = ref(null);
  const checkingAnswer = ref(false); // To disable Check button during API call
  
  const currentQuestionIndex = ref(0);
  const timeRemaining = ref(0);
  let timerInterval = null;
  
  const currentQuestion = computed(() => quiz.value.questions[currentQuestionIndex.value] || null);
  const progressPercentage = computed(() => quiz.value.questions.length > 0 ? (currentQuestionIndex.value / quiz.value.questions.length) * 100 : 0);
  const formattedTime = computed(() => {
    if (timeRemaining.value <= 0) return "00:00";
    const minutes = Math.floor(timeRemaining.value / 60);
    const seconds = timeRemaining.value % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  });
  
  const getOptionClass = (optionId) => {
    if (!currentQuestion.value) return '';
    const status = questionStatus[currentQuestion.value.id];
    if (!status || !status.checked) return '';
    
    const selectedOptionId = userAnswers[currentQuestion.value.id];
    
    if (status.isCorrect && optionId === selectedOptionId) {
      return 'option-correct';
    }
    if (!status.isCorrect) {
      if (optionId === selectedOptionId) return 'option-incorrect';
      if (optionId === status.correctOptionId) return 'option-actual-correct';
    }
    return '';
  };
  
  onMounted(async () => {
    try {
      const response = await userService.getQuizForAttempt(props.attemptId);
      quiz.value = { title: response.data.quiz_title, questions: response.data.questions || [] };
      response.data.questions.forEach(q => {
        questionStatus[q.id] = { checked: false, isCorrect: null, correctOptionId: null };
      });
      startTimer(response.data.time_remaining_seconds);
    } catch (err) {
      error.value = err.response?.data?.message || "Could not load the quiz.";
    } finally {
      loading.value = false;
    }
  });
  
  onUnmounted(() => clearInterval(timerInterval));
  
  const handleCheckAnswer = async () => {
    const qId = currentQuestion.value.id;
    const selectedOptId = userAnswers[qId];
    if (!selectedOptId) return;
  
    checkingAnswer.value = true;
    try {
      const res = await userService.checkAnswer(props.attemptId, qId, selectedOptId);
      questionStatus[qId] = {
        checked: true,
        isCorrect: res.data.correct,
        correctOptionId: res.data.correct_option_id
      };
    } catch (err) {
      alert("Error checking answer. Please try again.");
    } finally {
      checkingAnswer.value = false;
    }
  };
  
  const nextQuestion = () => {
    if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
      currentQuestionIndex.value++;
    }
  };
  
  const prevQuestion = () => {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--;
    }
  };
  
  const confirmSubmit = () => {
    if (confirm('Are you sure you want to submit your quiz?')) {
      submitQuiz();
    }
  };
  
  const startTimer = (seconds) => {
    timeRemaining.value = Math.max(0, Math.floor(seconds));
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      timeRemaining.value--;
      if (timeRemaining.value <= 0) {
        clearInterval(timerInterval);
        submitQuiz();
      }
    }, 1000);
  };
  
  const submitQuiz = async () => {
    if (quizResult.value) return;
    clearInterval(timerInterval);
    loading.value = true;
    try {
      const response = await userService.submitQuizAttempt(props.attemptId, userAnswers);
      quizResult.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.message || "An error occurred during submission.";
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .options-list .form-check-label {
    display: block;
    cursor: pointer;
    padding: 0.75rem 1.25rem;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
  }
  
  
  .options-list .form-check-input:checked + .form-check-label {
    background-color: #d1e7ff;
    border-color: #b6d4fe;
    font-weight: 500;
  }
  
  
  .options-list .form-check-label.option-correct {
    background-color: #d1e7dd !important; /* Bootstrap's light success green */
    border-color: #badbcc !important;
    color: #0f5132 !important;
  }
  
  
  .options-list .form-check-label.option-incorrect {
    background-color: #f8d7da !important; /* Bootstrap's light danger red */
    border-color: #f5c2c7 !important;
    color: #842029 !important;
  }
  
 
  .options-list .form-check-label.option-actual-correct {
    background-color: #d1e7dd !important; /* Bootstrap's light success green */
    border: 2px solid #198754 !important; /* A stronger green border to make it stand out */
    color: #0f5132 !important;
  }

  </style>