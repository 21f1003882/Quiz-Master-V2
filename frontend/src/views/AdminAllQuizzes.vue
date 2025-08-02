<template>
    <div>
      <h1 class="adminHeading mb-4">All Quizzes</h1>
  
      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Quiz List ({{ quizzes.length }})</span>
          <router-link :to="{ name: 'AdminAddQuiz' }" class="btn btn-success btn-sm">Add New Quiz</router-link>
        </div>
        <div class="card-body">
           <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Chapter</th>
                    <th>Subject</th>
                    <th>Duration</th>
                    <th>Active</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="quiz in quizzes" :key="quiz.id">
                    <td>{{ quiz.id }}</td>
                    <td>{{ quiz.title }}</td>
                    <td>{{ quiz.chapter_name }}</td>
                    <td>{{ quiz.subject_name }}</td>
                    <td>{{ quiz.duration_minutes }} min</td>
                    <td>
                      <span :class="quiz.is_active ? 'text-success' : 'text-danger'">
                        {{ quiz.is_active ? 'Yes' : 'No' }}
                      </span>
                    </td>
                    <td class="actions-cell">
                      <router-link :to="{ name: 'AdminManageQuestions', params: { quizId: quiz.id } }" class="btn btn-secondary btn-sm">Questions</router-link>
                      <router-link :to="{ name: 'AdminEditQuiz', params: { quizId: quiz.id } }" class="btn btn-primary btn-sm mx-1">Edit</router-link>
                      <form @submit.prevent="handleDeleteQuiz(quiz)" class="d-inline">
                        <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                      </form>
                    </td>
                  </tr>
                  <tr v-if="quizzes.length === 0">
                    <td colspan="7" class="text-center text-muted">No quizzes found.</td>
                  </tr>
                </tbody>
              </table>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import adminService from '@/services/adminService';
  
  const quizzes = ref([]);
  const loading = ref(true);
  const error = ref('');
  
  onMounted(async () => {
    try {
      const response = await adminService.getAllQuizzes();
      // The API response includes chapter_name and subject_name, so we can use it directly
      quizzes.value = response.data.quizzes || [];
    } catch (err) {
      console.error('Failed to fetch quizzes:', err);
      error.value = err.response?.data?.message || 'Could not load quizzes.';
    } finally {
      loading.value = false;
    }
  });
  
  const handleDeleteQuiz = async (quizToDelete) => {
    if (!confirm(`Delete quiz '${quizToDelete.title}' and ALL its questions/attempts?`)) {
      return;
    }
    try {
      await adminService.deleteQuiz(quizToDelete.id);
      quizzes.value = quizzes.value.filter(q => q.id !== quizToDelete.id);
    } catch (err) {
      console.error('Failed to delete quiz:', err);
      alert(err.response?.data?.message || 'Could not delete quiz.');
    }
  };
  
  function featureNotImplemented(featureName) {
    alert(`${featureName} feature is not implemented yet.`);
  }
  </script>
  
