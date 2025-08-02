// frontend/src/services/adminService.js
import apiClient from './apiClient'; // Import the configured Axios instance

export default {

  // === Subjects ===

  getSubjects() {
    return apiClient.get('/subjects/'); // Note trailing slash if Flask-RESTful adds it
  },

  getSubject(subjectId) {
    return apiClient.get(`/subjects/${subjectId}`);
  },


  addSubject(subjectData) {
    return apiClient.post('/subjects/', subjectData);
  },

  updateSubject(subjectId, subjectData) {
    return apiClient.put(`/subjects/${subjectId}`, subjectData);
  },

  deleteSubject(subjectId) {
    return apiClient.delete(`/subjects/${subjectId}`);
  },

  // === Chapters ===

  getChapter(chapterId) {
    return apiClient.get(`/chapters/${chapterId}`);
  },


  getChapters(subjectId = null) {
    const params = subjectId ? { subject_id: subjectId } : {};
    return apiClient.get('/chapters/', { params });
  },


  addChapter(chapterData) {
    return apiClient.post('/chapters/', chapterData);
  },

 
  updateChapter(chapterId, chapterData) {
    return apiClient.put(`/chapters/${chapterId}`, chapterData);
  },


  deleteChapter(chapterId) {
    return apiClient.delete(`/chapters/${chapterId}`);
  },

  // === Quizzes ===

  getQuiz(quizId) {
    return apiClient.get(`/quizzes/${quizId}`);
  },

  getQuizzes(chapterId = null) {
    const params = chapterId ? { chapter_id: chapterId } : {};
    return apiClient.get('/quizzes/', { params });
  },


   getAllQuizzes() {
    return apiClient.get('/quizzes/'); 
  },



  addQuiz(quizData) {
    return apiClient.post('/quizzes/', quizData);
  },


  updateQuiz(quizId, quizData) {
    return apiClient.put(`/quizzes/${quizId}`, quizData);
  },

 
  deleteQuiz(quizId) {
    return apiClient.delete(`/quizzes/${quizId}`);
  },

  // === Questions & Options ===

  getQuestion(questionId) {
    return apiClient.get(`/questions/${questionId}`);
  },

  getQuestionsForQuiz(quizId) {
    
    return apiClient.get(`/quizzes/${quizId}/questions`);
  },

 
  addQuestionWithOptions(quizId, questionData) {
    return apiClient.post(`/quizzes/${quizId}/questions`, questionData);
  },


  updateQuestionWithOptions(questionId, questionData) {
   
    return apiClient.put(`/questions/${questionId}`, questionData);
  },


  deleteQuestion(questionId) {
    return apiClient.delete(`/questions/${questionId}`);
  },



  getUsers() {
      return apiClient.get('/users/');
  },


  getAttempts(userId = null) {
      const params = userId ? { user_id: userId } : {};
      return apiClient.get('/attempts/', { params });
  },

  getAdminSummaryData() {
    return apiClient.get('/summary/');
  },

  getUserActivity(userId) {
    return apiClient.get(`/admin/users/${userId}/activity`);
  },

  //=== Search ===

  search(query) {
    // This calls your new API endpoint: GET /api/search/?q=...
    return apiClient.get('/search/', { params: { q: query } });
  },

};
