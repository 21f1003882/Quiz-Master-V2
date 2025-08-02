<template>
    <div>
      <h1 class="userHeading mb-4">My Quiz Summary</h1>
  
      <div v-if="loading" class="d-flex justify-content-center my-5">
        <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
  
      <div v-else>
        <!-- Export Section -->
        <div class="d-flex justify-content-end mb-4">
          <button class="btn btn-outline-dark" @click="handleExport" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
            {{ exportStatusMessage }}
          </button>
        </div>
  
        <!-- Charts Row -->
        <div class="row gy-4">
          <div class="col-md-6">
            <div class="card shadow-sm h-100">
              <div class="card-header">My Highest Scores per Subject (%)</div>
              <div class="summary-card-body">
                <BarChart v-if="summary.chart_data.top_scores.labels.length" :chartData="topScoresChartData" />
                <p v-else class="text-muted text-center mt-5">No score data to display.</p>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm h-100">
              <div class="card-header">My Average Attempts per Subject (%)</div>
              <div class="summary-card-body d-flex justify-content-center align-items-center">
                <DoughnutChart v-if="summary.chart_data.attempts.labels.length" :chartData="attemptsChartData" />
                <p v-else class="text-muted text-center">No attempt data to display.</p>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Past Attempts Table -->
        <h3 class="mt-5 mb-3">Past Attempts</h3>
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Quiz Title</th>
                    <th>Subject</th>
                    <th>Score</th>
                    <th>Percentage</th>
                    <th>Date Submitted</th>
                    <th>Time Taken</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(attempt, index) in summary.attempts" :key="index">
                    <td>{{ attempt.quiz_title }}</td>
                    <td>{{ attempt.subject_name }}</td>
                    <td>{{ attempt.score }} / {{ attempt.total_questions }}</td>
                    <td>{{ attempt.percentage_score.toFixed(1) }}%</td>
                    <td>{{ attempt.submitted_at }}</td>
                    <td>{{ attempt.time_taken }}</td>
                  </tr>
                  <tr v-if="!summary.attempts.length">
                    <td colspan="6" class="text-center text-muted p-4">You haven't completed any quizzes yet.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, computed, onUnmounted } from 'vue';
  import userService from '@/services/userService';
  import BarChart from '@/components/charts/BarChart.vue';
  import DoughnutChart from '@/components/charts/DoughnutChart.vue';
  
  const loading = ref(true);
  const error = ref('');
  const summary = reactive({
    attempts: [],
    chart_data: { top_scores: {labels:[], data:[]}, attempts: {labels:[], data:[]} },
  });
  
  // State for the export feature
  const exporting = ref(false);
  const exportStatusMessage = ref("Export My Attempts as CSV");
  let pollingInterval = null;
  
  // Chart.js color palettes
  const userPalette1 = ['#1abc9c', '#3498db', '#9b59b6', '#f1c40f', '#e67e22', '#e74c3c'];
  const userPalette2 = ['rgba(26, 188, 156, 0.8)', 'rgba(52, 152, 219, 0.8)', 'rgba(155, 89, 182, 0.8)', 'rgba(241, 196, 15, 0.8)', 'rgba(230, 126, 34, 0.8)', 'rgba(231, 76, 60, 0.8)'];
  
  const topScoresChartData = computed(() => ({
    labels: summary.chart_data.top_scores.labels,
    datasets: [{ label: 'My Highest Score (%)', data: summary.chart_data.top_scores.data, backgroundColor: userPalette2 }]
  }));
  const attemptsChartData = computed(() => ({
    labels: summary.chart_data.attempts.labels,
    datasets: [{ label: 'My Average Attempts (%)', data: summary.chart_data.attempts.data, backgroundColor: userPalette1 }]
  }));
  
  onMounted(async () => {
    try {
      const response = await userService.getSummaryData();
      Object.assign(summary, response.data);
    } catch (err) {
      error.value = err.response?.data?.message || "Could not load summary data.";
    } finally {
      loading.value = false;
    }
  });
  
  onUnmounted(() => {
    // Clean up the polling interval if the user navigates away
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
  });
  
  const handleExport = async () => {
    exporting.value = true;
    exportStatusMessage.value = "Generating report...";
    try {
      const response = await userService.startCsvExport();
      const taskId = response.data.task_id;
      pollForExportStatus(taskId);
    } catch (err) {
      exporting.value = false;
      exportStatusMessage.value = "Export My Attempts as CSV";
      alert("Failed to start the export job.");
    }
  };
  
  const pollForExportStatus = (taskId) => {
    pollingInterval = setInterval(async () => {
      try {
        const response = await userService.getExportStatus(taskId);
        const status = response.data.status;
  
        if (status === 'SUCCESS') {
          clearInterval(pollingInterval);
          exporting.value = false;
          exportStatusMessage.value = "Export My Attempts as CSV";
          
          const result = response.data.result;
          if (result.status === 'SUCCESS') {
            const filename = result.filename;
            alert("Your CSV export is ready!");
            // Trigger the download by creating a temporary link
            window.location.href = `/api/exports/${filename}`;
          } else {
            alert(`There was an error generating your report: ${result.error}`);
          }
  
        } else if (status === 'FAILURE') {
          clearInterval(pollingInterval);
          exporting.value = false;
          exportStatusMessage.value = "Export My Attempts as CSV";
          alert("There was a critical error generating your report.");
        }
        // If status is PENDING or other intermediate states, do nothing and let the interval run again.
      } catch (err) {
        clearInterval(pollingInterval);
        exporting.value = false;
        exportStatusMessage.value = "Export My Attempts as CSV";
        alert("Could not check the status of your export job.");
      }
    }, 3000); // Check every 3 seconds
  };
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