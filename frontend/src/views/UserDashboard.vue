<template>
  <div>
    <h1 class="userHeading mb-4">Available Quizzes</h1>

    <div v-if="loading" class="d-flex justify-content-center my-5">
      <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="subjects.length === 0" class="text-center text-muted mt-5">
      <p>No quizzes are available at the moment. Please check back later!</p>
    </div>

    <div v-else class="accordion" id="subjectsAccordionUser">
      <div v-for="subject in subjects" :key="subject.id" class="accordion-item mb-3 border-0">
        <h2 class="accordion-header" :id="'heading' + subject.id">
          <button class="accordion-button subject-accordion-button-user collapsed" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + subject.id">
            {{ subject.name }}
          </button>
        </h2>
        <div :id="'collapse' + subject.id" class="accordion-collapse collapse" data-bs-parent="#subjectsAccordionUser">
          <div class="accordion-body border rounded-bottom">
            <p v-if="subject.description" class="small mb-3"><em>{{ subject.description }}</em></p>

            <div v-for="chapter in subject.chapters" :key="chapter.id" class="mb-4">
              <h5 class="chapter-header">{{ chapter.name }}</h5>
              <div class="row g-3">
                <div v-for="quiz in chapter.quizzes" :key="quiz.id" class="col-md-6 col-lg-4">
                  <div class="card h-100 quiz-card">
                    <div class="card-body">
                      <h6 class="card-title">{{ quiz.title }}</h6>
                      <h6 class="card-subtitle mb-2 text-muted">Duration: {{ quiz.duration_minutes }} min</h6>
                    </div>
                    <div class="card-footer text-center">
                      <button class="btn btn-primary" @click="handleStartQuiz(quiz.id)" :disabled="startingQuizId === quiz.id">
                        <span v-if="startingQuizId === quiz.id" class="spinner-border spinner-border-sm"></span>
                        <span v-else>Attempt Quiz</span>
                      </button>
                      <span v-if="highScores[quiz.id]" class="badge bg-info ms-2" title="Your highest score">
                        Highest: {{ highScores[quiz.id].score }}/{{ highScores[quiz.id].total }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import userService from '@/services/userService';

const router = useRouter();

const loading = ref(true);
const error = ref('');
const subjects = ref([]);
const highScores = ref({});
const startingQuizId = ref(null); // To show a spinner on the specific button clicked

onMounted(async () => {
  try {
    const response = await userService.getDashboardData();
    subjects.value = response.data.subjects;
    highScores.value = response.data.high_scores;
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
    error.value = err.response?.data?.message || "Could not load dashboard.";
  } finally {
    loading.value = false;
  }
});

const handleStartQuiz = async (quizId) => {
  startingQuizId.value = quizId;
  try {
    const response = await userService.startQuiz(quizId);
    const attemptId = response.data.attempt_id;
    // Redirect to the AttendQuiz page with the new attempt ID
    router.push({ name: 'AttendQuiz', params: { attemptId } });
  } catch (err) {
    console.error("Failed to start quiz:", err);
    // You could show a more specific error to the user here
    alert(err.response?.data?.message || "Could not start the quiz.");
  } finally {
    startingQuizId.value = null;
  }
};
</script>

<style scoped>
/* Scoped styles from your original CSS for the user dashboard */
.subject-accordion-button-user {
  background: linear-gradient(135deg, #0b0710 0%, #09101d 100%); 
  color: white !important; 
  border-radius: 0.5rem !important;
  font-weight: 500; 
}
.subject-accordion-button-user:not(.collapsed) {
  background: linear-gradient(135deg, #5e0ead 0%, #073788 100%);
}
.subject-accordion-button-user::after {
  filter: brightness(0) invert(1);
}
.accordion-body {
  background-color: #e9d4ff; 
}
.chapter-header {
  font-weight: 500;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #d1b3ff;
}
.quiz-card {
  transition: transform .2s ease-in-out;
}
.quiz-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.card-footer {
  background-color: #f8f9fa;
}
</style>