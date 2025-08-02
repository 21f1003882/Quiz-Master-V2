<template>
    <div>
      <div v-if="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
  
      <div v-else>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><router-link :to="{ name: 'AdminDashboard' }">Admin Dashboard</router-link></li>
            <li class="breadcrumb-item"><router-link :to="{ name: 'AdminSummary' }">Summary</router-link></li>
            <li class="breadcrumb-item active" aria-current="page">User Activity</li>
          </ol>
        </nav>
  
        <h1 class="mb-4">User Activity: {{ activity.user.username }}</h1>
        <p><strong>Email:</strong> {{ activity.user.email }}</p>
  
        <div class="card shadow-sm">
          <div class="card-header">Quiz Attempt History</div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover table-sm">
                <thead>
                  <tr>
                    <th>Quiz Title</th>
                    <th>Chapter</th>
                    <th>Subject</th>
                    <th>Score</th>
                    <th>Percentage</th>
                    <th>Date Submitted</th>
                    <th>Time Taken</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(attempt, index) in activity.attempts" :key="index">
                    <td>{{ attempt.quiz_title }}</td>
                    <td>{{ attempt.chapter_name }}</td>
                    <td>{{ attempt.subject_name }}</td>
                    <td>{{ attempt.score }} / {{ attempt.total_questions }}</td>
                    <td>{{ attempt.percentage_score.toFixed(1) }}%</td>
                    <td>{{ attempt.submitted_at }}</td>
                    <td>{{ attempt.time_taken }}</td>
                  </tr>
                  <tr v-if="!activity.attempts.length">
                    <td colspan="7" class="text-center text-muted p-4">
                      {{ activity.user.username }} hasn't completed any quizzes yet.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
  
        <div class="mt-4">
          <router-link :to="{ name: 'AdminSummary' }" class="btn btn-secondary">&laquo; Back to Summary</router-link>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue';
  import adminService from '@/services/adminService';
  
  const props = defineProps({
    userId: {
      type: [String, Number],
      required: true
    }
  });
  
  const loading = ref(true);
  const error = ref('');
  const activity = reactive({
    user: {},
    attempts: []
  });
  
  onMounted(async () => {
    try {
      const response = await adminService.getUserActivity(props.userId);
      Object.assign(activity, response.data);
    } catch (err) {
      console.error("Failed to load user activity:", err);
      error.value = err.response?.data?.message || "Could not load user activity data.";
    } finally {
      loading.value = false;
    }
  });
  </script>
  
  <style scoped>
  .breadcrumb-item a {
    text-decoration: none;
  }
  </style>