// src/services/userService.js
import apiClient from './apiClient';

export default {
    startCsvExport() {
        return apiClient.post('/user/export-attempts');
      },
      getExportStatus(taskId) {
        return apiClient.get(`/tasks/${taskId}/status`);
      },
  getDashboardData() { return apiClient.get('/user/dashboard-data'); },
  startQuiz(quizId) { return apiClient.post(`/user/quizzes/${quizId}/start`); },
  getQuizForAttempt(attemptId) { return apiClient.get(`/user/attempts/${attemptId}`); },
  submitQuizAttempt(attemptId, answers) { return apiClient.post(`/user/attempts/${attemptId}`, { answers }); },
  getSummaryData() {return apiClient.get('/user/summary-data');},
  checkAnswer(attemptId, questionId, selectedOptionId) {
    return apiClient.post(`/user/attempts/${attemptId}/check`, {
      question_id: questionId,
      selected_option_id: selectedOptionId
    });
  }
};