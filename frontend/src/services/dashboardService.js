// frontend/src/services/dashboardService.js

import apiClient from './apiClient';

export default {
  getUserDashboardData() {
    console.log("dashboardService: Using apiClient:", apiClient); 
    if (typeof apiClient?.get !== 'function') {
        const errorMsg = "API client not configured correctly in dashboardService";
        console.error(errorMsg);
        return Promise.reject(new Error(errorMsg));
    }

     return Promise.all([
        apiClient.get('/subjects/'), 
        apiClient.get('/attempts/') 
    ]).then(([subjectsResponse, attemptsResponse]) => {
        const high_scores = {};
        
        (attemptsResponse.data.attempts || []).forEach(att => {
            if (!high_scores[att.quiz_id] || att.score > high_scores[att.quiz_id].score) {
                high_scores[att.quiz_id] = { score: att.score, total: att.total_questions };
            }
        });
        return { data: { subjects: subjectsResponse.data.subjects || [], high_scores: high_scores } };
    });
  }
}