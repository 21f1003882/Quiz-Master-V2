<template>
    <div>
      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else>
        <h1 class="mb-4">Add New Quiz</h1>
  
        <form @submit.prevent="handleAddQuiz">
          <!-- Quiz Title -->
          <div class="mb-3">
            <label for="quizTitle" class="form-label">Quiz Title</label>
            <input type="text" id="quizTitle" class="form-control" v-model="newQuiz.title" required>
          </div>
  
          <!-- Chapter Selection -->
          <div class="mb-3">
            <label for="quizChapter" class="form-label">Chapter</label>
            <select id="quizChapter" class="form-select" v-model="newQuiz.chapter_id" required>
              <option :value="null" disabled>-- Select a Chapter --</option>
              <option v-for="chapter in allChapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.subject_name }} - {{ chapter.name }}
              </option>
            </select>
          </div>
  
          <!-- Duration -->
          <div class="mb-3">
            <label for="quizDuration" class="form-label">Duration (minutes)</label>
            <input type="number" id="quizDuration" class="form-control" v-model="newQuiz.duration_minutes" required min="1">
          </div>
  
          <!-- Is Active Checkbox -->
          <div class="mb-3 form-check">
            <input type="checkbox" id="quizIsActive" class="form-check-input" v-model="newQuiz.is_active">
            <label for="quizIsActive" class="form-check-label">Is Active</label>
          </div>
          
          <div v-if="addError" class="alert alert-danger mt-3">{{ addError }}</div>
  
          <div class="mt-4">
            <button type="submit" class="btn btn-success" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
              {{ isSubmitting ? 'Adding Quiz...' : 'Add Quiz and Manage Questions' }}
            </button>
            <router-link :to="{ name: 'AdminDashboard' }" class="btn btn-secondary ms-2">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import adminService from '@/services/adminService';
  
  const router = useRouter();
  const route = useRoute();
  
  // State
  const loading = ref(true);
  const error = ref('');
  const allChapters = ref([]);
  
  const newQuiz = reactive({
    title: '',
    chapter_id: null,
    duration_minutes: 15,
    is_active: true
  });
  
  const isSubmitting = ref(false);
  const addError = ref('');
  
  // On component mount, fetch all chapters for the dropdown
  onMounted(async () => {
    try {
      const response = await adminService.getChapters();
      allChapters.value = response.data.chapters;
      
      // Check if a chapterId was passed in the URL to pre-select it
      const preselectChapterId = parseInt(route.query.chapterId);
      if (preselectChapterId && allChapters.value.some(c => c.id === preselectChapterId)) {
        newQuiz.chapter_id = preselectChapterId;
      }
  
    } catch (err) {
      console.error('Failed to fetch chapters:', err);
      error.value = err.response?.data?.message || 'Could not load chapter data.';
    } finally {
      loading.value = false;
    }
  });
  
  // Handle the form submission
  const handleAddQuiz = async () => {
    isSubmitting.value = true;
    addError.value = '';
    try {
      const response = await adminService.addQuiz(newQuiz);
      const createdQuiz = response.data;
      
      // On success, redirect to the question management page for the newly created quiz
      router.push({ name: 'AdminManageQuestions', params: { quizId: createdQuiz.id } });
      alert('Quiz added successfully! Now you can add questions.');
  
    } catch (err) {
      console.error('Failed to add quiz:', err);
      addError.value = err.response?.data?.message || 'An error occurred while creating the quiz.';
    } finally {
      isSubmitting.value = false;
    }
  };
  </script>
  
  <style scoped>
  form {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    background-color: #f8f9fa;
    border-radius: 0.5rem;
  }
  </style>