<template>
    <div>
      <div v-if="loading" class="text-center my-5"><div class="spinner-border" role="status"></div></div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><router-link :to="{ name: 'AdminDashboard' }">Admin Dashboard</router-link></li>
            <li class="breadcrumb-item active" aria-current="page">Quiz: {{ quiz.title }}</li>
          </ol>
        </nav>
        <br>
        <h1 class="mb-2">Manage Questions: {{ quiz.title }}</h1>
        <h5 class="mb-4 text-muted">{{ quiz.chapter_name }} | {{ quiz.subject_name }}</h5>
  
        <div class="card mb-4 border-success">
          <div class="card-header bg-success text-white">Add New Question</div>
          <div class="card-body">
            <form @submit.prevent="handleAddQuestion">
              <div class="mb-3">
                <label for="newQuestionText" class="form-label">Question Text</label>
                <textarea id="newQuestionText" class="form-control" v-model="newQuestion.text" rows="3" required></textarea>
              </div>
              <div class="row mb-3">
                <div class="col-md-6 mb-2" v-for="i in 4" :key="i">
                  <label :for="'option'+i" class="form-label">Option {{ i }}</label>
                  <input type="text" :id="'option'+i" class="form-control" v-model="newQuestion.options[i-1]" required>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Correct Option</label>
                <div>
                  <div v-for="i in 4" :key="i" class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" :id="'correct'+i" :value="i" v-model="newQuestion.correct_option_index" required>
                    <label class="form-check-label" :for="'correct'+i">Option {{ i }}</label>
                  </div>
                </div>
              </div>
              <div v-if="addError" class="alert alert-danger">{{ addError }}</div>
              <button type="submit" class="btn btn-success" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
                {{ isSubmitting ? 'Adding...' : 'Add Question' }}
              </button>
            </form>
          </div>
        </div>
  
        <h3 class="mt-5 mb-3">Existing Questions ({{ questions.length }})</h3>
        <div v-if="questions.length">
          <div v-for="(question, index) in questions" :key="question.id" class="card mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <p class="card-text mb-1"><strong>Q{{ index + 1 }}:</strong> {{ question.text }}</p>
                <div>
                    <router-link :to="{ name: 'AdminEditQuestion', params: { questionId: question.id } }" class="btn btn-sm btn-outline-primary">Edit</router-link>
                  <button @click="handleDeleteQuestion(question.id)" class="btn btn-sm btn-outline-danger ms-2">Delete</button>
                </div>
              </div>
              <ul class="list-group list-group-flush mt-2">
                <li v-for="(option, optIndex) in question.options" :key="option.id" class="list-group-item" :class="{'list-group-item-success': option.is_correct}">
                  {{ optIndex + 1 }}. {{ option.text }}
                  <span v-if="option.is_correct" class="badge bg-success float-end">Correct</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <p v-else class="text-muted">No questions have been added to this quiz yet.</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue';
  import adminService from '@/services/adminService';
  
  const props = defineProps({
    quizId: { type: String, required: true }
  });
  
  // State for page data
  const quiz = ref({});
  const questions = ref([]);
  const loading = ref(true);
  const error = ref('');
  
  // State for the "Add Question" form
  const newQuestion = reactive({
    text: '',
    options: ['', '', '', ''],
    correct_option_index: null
  });
  const isSubmitting = ref(false);
  const addError = ref('');
  
  // Fetch all necessary data when the component loads
  onMounted(async () => {
    try {
      const [quizRes, questionsRes] = await Promise.all([
        adminService.getQuiz(props.quizId),
        adminService.getQuestionsForQuiz(props.quizId)
      ]);
      quiz.value = quizRes.data;
      questions.value = questionsRes.data.questions;
    } catch (err) {
      console.error('Failed to load page data:', err);
      error.value = err.response?.data?.message || 'Could not load quiz data.';
    } finally {
      loading.value = false;
    }
  });
  
  // Handler to add a new question
  const handleAddQuestion = async () => {
    isSubmitting.value = true;
    addError.value = '';
    try {
      const payload = {
        text: newQuestion.text,
        options: newQuestion.options,
        correct_option_index: parseInt(newQuestion.correct_option_index)
      };
      const response = await adminService.addQuestionWithOptions(props.quizId, payload);
      questions.value.push(response.data); // Add new question to the list
      
      // Reset the form
      Object.assign(newQuestion, { text: '', options: ['', '', '', ''], correct_option_index: null });
  
    } catch (err) {
      console.error('Failed to add question:', err);
      addError.value = err.response?.data?.message || 'An error occurred.';
    } finally {
      isSubmitting.value = false;
    }
  };
  
  // Handler to delete a question
  const handleDeleteQuestion = async (questionId) => {
    if (!confirm('Are you sure you want to delete this question?')) return;
    try {
      await adminService.deleteQuestion(questionId);
      // Remove the question from the local list without a full refresh
      questions.value = questions.value.filter(q => q.id !== questionId);
    } catch (err) {
      console.error('Failed to delete question:', err);
      alert(err.response?.data?.message || 'Could not delete question.');
    }
  };
  
  function featureNotImplemented(featureName) {
    alert(`${featureName} feature will be implemented next!`);
  }
  </script>
  
