<template>
    <div>
      <h1 class="adminHeading mb-4">Admin Summary</h1>
  
      <div v-if="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
  
      <div v-else>
        <div class="row gy-4">
          <div class="col-md-6">
            <div class="card shadow-sm h-100">
              <div class="card-header">Highest Scores per Subject</div>
              <div class="summary-card-body">
                  <BarChart v-if="summary.chart_data.top_scores.labels.length" :chartData="topScoresChartData" />
                  <p v-else class="text-muted text-center mt-5">No score data available.</p>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm h-100">
              <div class="card-header">Total Attempts per Subject</div>
              <div class="summary-card-body d-flex justify-content-center align-items-center">
                  <DoughnutChart v-if="summary.chart_data.attempts.labels.length" :chartData="attemptsChartData" />
                  <p v-else class="text-muted text-center">No attempt data available.</p>
              </div>
            </div>
          </div>
          <div class="col-md-12 mt-4">
            <div class="card shadow-sm">
              <div class="card-header">Number of Quizzes per Subject</div>
              <div class="summary-card-body">
                  <BarChart v-if="summary.chart_data.quiz_count.labels.length" :chartData="quizCountChartData" />
                  <p v-else class="text-muted text-center mt-5">No quiz data available.</p>
              </div>
            </div>
          </div>
        </div>
  
        <h3 class="mt-5 mb-3">Content Overview</h3>
        <div class="row g-3 mb-4 text-white">
          <div class="col-lg col-md-4 col-6"><div class="card text-center bg-primary h-100"><div class="card-body py-4"><h5 class="card-title display-6">{{ summary.content_counts.users }}</h5><p class="card-text">Total Users</p></div></div></div>
          <div class="col-lg col-md-4 col-6"><div class="card text-center bg-success h-100"><div class="card-body py-4"><h5 class="card-title display-6">{{ summary.content_counts.subjects }}</h5><p class="card-text">Total Subjects</p></div></div></div>
          <div class="col-lg col-md-4 col-4"><div class="card text-center bg-info text-dark h-100"><div class="card-body py-4"><h5 class="card-title display-6">{{ summary.content_counts.chapters }}</h5><p class="card-text">Chapters</p></div></div></div>
          <div class="col-lg col-md-6 col-4"><div class="card text-center bg-warning text-dark h-100"><div class="card-body py-4"><h5 class="card-title display-6">{{ summary.content_counts.quizzes }}</h5><p class="card-text">Quizzes</p></div></div></div>
          <div class="col-lg col-md-6 col-4"><div class="card text-center bg-secondary h-100"><div class="card-body py-4"><h5 class="card-title display-6">{{ summary.content_counts.questions }}</h5><p class="card-text">Questions</p></div></div></div>
        </div>
  
        <h3 class="mt-5 mb-3">User Activity Ranking</h3>
        <div class="card shadow-sm mb-4">
          <div class="card-header">Users Ranked by Quiz Attempts</div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped table-hover">
                <thead><tr><th>Rank</th><th>Username</th><th>Email</th><th>Attempts</th><th>View Activity</th></tr></thead>
                <tbody>
                  <tr v-for="(user, index) in summary.user_activity" :key="user.id">
                    <td>{{ index + 1 }}</td><td>{{ user.username }}</td><td>{{ user.email }}</td><td>{{ user.attempt_count }}</td>
                    <td>
                        <router-link :to="{ name: 'AdminUserActivity', params: { userId: user.id } }" class="btn btn-sm btn-outline-info">View</router-link>
                    </td>
                  </tr>
                  <tr v-if="!summary.user_activity.length"><td colspan="5" class="text-center text-muted">No user activity found.</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
  
        <h3 class="mt-5 mb-3">Incomplete Quizzes</h3>
        <div class="card shadow-sm mb-4">
          <div class="card-header">Quizzes Without Any Questions</div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped table-hover">
                <thead><tr><th>Quiz Title</th><th>Chapter</th><th>Subject</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="quiz in summary.quizzes_no_questions" :key="quiz.id">
                    <td>{{ quiz.title }}</td><td>{{ quiz.chapter_name }}</td><td>{{ quiz.subject_name }}</td>
                    <td>
                      <router-link :to="{ name: 'AdminManageQuestions', params: { quizId: quiz.id } }" class="btn btn-sm btn-primary">Add Questions</router-link>
                      <router-link :to="{ name: 'AdminEditQuiz', params: { quizId: quiz.id } }" class="btn btn-sm btn-outline-secondary ms-1">Edit Quiz</router-link>
                    </td>
                  </tr>
                  <tr v-if="!summary.quizzes_no_questions.length"><td colspan="4" class="text-center text-muted">All quizzes have at least one question.</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, computed } from 'vue';
  import adminService from '@/services/adminService';
  import BarChart from '@/components/charts/BarChart.vue';
  import DoughnutChart from '@/components/charts/DoughnutChart.vue';
  
  const loading = ref(true);
  const error = ref('');
  const summary = reactive({
    chart_data: { top_scores: {}, attempts: {}, quiz_count: {} },
    content_counts: {},
    user_activity: [],
    quizzes_no_questions: []
  });
  
  const colorPalette1 = ['#2575fc', '#6a11cb', '#fecf4f', '#fc6a4f', '#4ffecf', '#cf4fec'];
  const colorPalette2 = ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40'];
  
  const topScoresChartData = computed(() => ({
    labels: summary.chart_data.top_scores.labels,
    datasets: [{ label: 'Highest Score', data: summary.chart_data.top_scores.data, backgroundColor: colorPalette1 }]
  }));
  const attemptsChartData = computed(() => ({
    labels: summary.chart_data.attempts.labels,
    datasets: [{ label: 'Total Attempts', data: summary.chart_data.attempts.data, backgroundColor: colorPalette2 }]
  }));
  const quizCountChartData = computed(() => ({
    labels: summary.chart_data.quiz_count.labels,
    datasets: [{ label: 'Number of Quizzes', data: summary.chart_data.quiz_count.data, backgroundColor: colorPalette1 }]
  }));
  
  onMounted(async () => {
    try {
      const response = await adminService.getAdminSummaryData();
      Object.assign(summary, response.data);
    } catch (err) {
      error.value = err.response?.data?.message || "Could not load summary data.";
    } finally {
      loading.value = false;
    }
  });
  
  function featureNotImplemented(featureName) {
    alert(`${featureName} feature is not implemented yet.`);
  }
  </script>
  
  <style scoped>
  .summary-card-body {
    padding: 1rem;
    height: 265px;
    background-color: #f8f9fa;
  }
  .card-header {
    font-weight: 500;
  }
  </style>