<template>
    <div>
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else>
        <h1 class="mb-4">Edit Quiz</h1>
        <h5 class="mb-3 text-muted">Editing: {{ initialQuizTitle }}</h5>
  
        <form @submit.prevent="handleUpdate">
          <div class="mb-3">
            <label for="quizTitle" class="form-label">Quiz Title</label>
            <input type="text" id="quizTitle" class="form-control" v-model="quiz.title" required>
          </div>
  
          <div class="mb-3">
            <label for="quizChapter" class="form-label">Chapter</label>
            <select id="quizChapter" class="form-select" v-model="quiz.chapter_id" required>
              <option v-for="chapter in allChapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.subject_name }} - {{ chapter.name }}
              </option>
            </select>
          </div>
  
          <div class="mb-3">
            <label for="quizDuration" class="form-label">Duration (minutes)</label>
            <input type="number" id="quizDuration" class="form-control" v-model="quiz.duration_minutes" required min="1">
          </div>
  
          <div class="mb-3 form-check">
            <input type="checkbox" id="quizIsActive" class="form-check-input" v-model="quiz.is_active">
            <label for="quizIsActive" class="form-check-label">Is Active</label>
          </div>
          
          <div v-if="updateError" class="alert alert-danger mt-3">{{ updateError }}</div>
  
          <div class="mt-4">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>
            <router-link :to="{ name: 'AdminDashboard' }" class="btn btn-secondary ms-2">Cancel</router-link>
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
    quizId: {
      type: String,
      required: true
    }
  });
  
  const router = useRouter();
  
  // State
  const loading = ref(true);
  const error = ref('');
  const initialQuizTitle = ref('');
  const allChapters = ref([]);
  
  const quiz = reactive({
    title: '',
    chapter_id: null,
    duration_minutes: 10,
    is_active: true
  });
  
  const isSubmitting = ref(false);
  const updateError = ref('');
  
  // On component mount, fetch both the quiz data and the list of all chapters
  onMounted(async () => {
    try {
      // Perform API calls in parallel for efficiency
      const [quizRes, chaptersRes] = await Promise.all([
        adminService.getQuiz(props.quizId),
        adminService.getChapters() // Get all chapters for the dropdown
      ]);
      
      // Populate form data from the specific quiz
      const fetchedQuiz = quizRes.data;
      quiz.title = fetchedQuiz.title;
      quiz.chapter_id = fetchedQuiz.chapter_id;
      quiz.duration_minutes = fetchedQuiz.duration_minutes;
      quiz.is_active = fetchedQuiz.is_active;
  
      initialQuizTitle.value = fetchedQuiz.title;
  
      // Populate the dropdown options
      allChapters.value = chaptersRes.data.chapters;
  
    } catch (err) {
      console.error('Failed to fetch data:', err);
      error.value = err.response?.data?.message || 'Quiz or chapter data could not be loaded.';
    } finally {
      loading.value = false;
    }
  });
  
  // Handle the form submission
  const handleUpdate = async () => {
    isSubmitting.value = true;
    updateError.value = '';
    try {
      await adminService.updateQuiz(props.quizId, quiz);
      router.push({ name: 'AdminDashboard' });
      alert('Quiz updated successfully!');
    } catch (err) {
      console.error('Failed to update quiz:', err);
      updateError.value = err.response?.data?.message || 'An error occurred while updating.';
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