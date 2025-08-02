<template>
    <div>
      <div v-if="loading" class="text-center my-5"><div class="spinner-border" role="status"></div></div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><router-link :to="{ name: 'AdminDashboard' }">Admin Dashboard</router-link></li>
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'AdminManageQuestions', params: { quizId: question.quiz_id } }">Quiz: {{ quizTitle }}</router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">Edit Question</li>
          </ol>
        </nav>
  
        <h1 class="mb-4">Edit Question</h1>
  
        <form @submit.prevent="handleUpdate">
          <div class="mb-3">
            <label for="questionText" class="form-label">Question Text</label>
            <textarea id="questionText" class="form-control" v-model="formState.text" rows="3" required></textarea>
          </div>
          <div class="row mb-3">
            <div class="col-md-6 mb-2" v-for="i in 4" :key="i">
              <label :for="'option'+i" class="form-label">Option {{ i }}</label>
              <input type="text" :id="'option'+i" class="form-control" v-model="formState.options[i-1]" required>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Correct Option</label>
            <div>
              <div v-for="i in 4" :key="i" class="form-check form-check-inline">
                <input class="form-check-input" type="radio" :id="'correct'+i" :value="i" v-model="formState.correct_option_index" required>
                <label class="form-check-label" :for="'correct'+i">Option {{ i }}</label>
              </div>
            </div>
          </div>
          <div v-if="updateError" class="alert alert-danger">{{ updateError }}</div>
          <div class="mt-4">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>
            <router-link :to="{ name: 'AdminManageQuestions', params: { quizId: question.quiz_id } }" class="btn btn-secondary ms-2">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import adminService from '@/services/adminService';
  
  const props = defineProps({
    questionId: { type: String, required: true }
  });
  
  const router = useRouter();
  
  // State
  const loading = ref(true);
  const error = ref('');
  const question = ref({}); // Will hold the full question object from API
  const quizTitle = ref(''); // To display in breadcrumbs
  
  // The state for our form, separated for clarity
  const formState = reactive({
    text: '',
    options: ['', '', '', ''],
    correct_option_index: null
  });
  
  const isSubmitting = ref(false);
  const updateError = ref('');
  
  onMounted(async () => {
    try {
      const response = await adminService.getQuestion(props.questionId);
      question.value = response.data;
  
      // Populate the form state from the fetched data
      formState.text = question.value.text;
      formState.options = question.value.options.map(opt => opt.text);
      
      // Find the 1-based index of the correct option
      const correctIndex = question.value.options.findIndex(opt => opt.is_correct);
      if (correctIndex !== -1) {
        formState.correct_option_index = correctIndex + 1;
      }
  
      // Fetch quiz details for the breadcrumb title
      const quizResponse = await adminService.getQuiz(question.value.quiz_id);
      quizTitle.value = quizResponse.data.title;
  
    } catch (err) {
      console.error('Failed to load question data:', err);
      error.value = err.response?.data?.message || 'Could not load question data.';
    } finally {
      loading.value = false;
    }
  });
  
  const handleUpdate = async () => {
    isSubmitting.value = true;
    updateError.value = '';
    try {
      // The payload must match what the API expects
      const payload = {
        text: formState.text,
        options: formState.options,
        correct_option_index: parseInt(formState.correct_option_index)
      };
      await adminService.updateQuestionWithOptions(props.questionId, payload);
      
      // On success, navigate back to the question list for that quiz
      router.push({ name: 'AdminManageQuestions', params: { quizId: question.value.quiz_id } });
      alert('Question updated successfully!');
    } catch (err) {
      console.error('Failed to update question:', err);
      updateError.value = err.response?.data?.message || 'An error occurred.';
    } finally {
      isSubmitting.value = false;
    }
  };
  </script>