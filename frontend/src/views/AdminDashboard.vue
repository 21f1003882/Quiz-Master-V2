<template>
  <div>
    <h1 class="adminHeading mb-4">Admin Dashboard</h1>

    <div v-if="loading" class="d-flex justify-content-center my-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else>
      <h4 class="mb-4 adminHeading">Welcome, {{ auth.user?.username || 'Admin' }}!</h4>

      <div class="card add-subject-section mb-4">
        <h5 class="card-title mb-3">Add New Subject</h5>
        <form @submit.prevent="addSubjectHandler" class="row g-3 align-items-end">
          <div class="col-md-5">
            <input type="text" v-model="newSubject.name" class="form-control" placeholder="New Subject Name" required>
          </div>
          <div class="col-md-5">
            <textarea v-model="newSubject.description" class="form-control" placeholder="Optional Description" rows="1"></textarea>
          </div>
          <div class="col-md-2">
            <button type="submit" class="btn btn-success w-100" :disabled="addSubjectLoading">
              <span v-if="addSubjectLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ addSubjectLoading ? ' Adding...' : 'Add Subject' }}
            </button>
          </div>
        </form>
        <div v-if="addSubjectError" class="alert alert-danger mt-3 mb-0">{{ addSubjectError }}</div>
      </div>

      <div class="accordion" id="subjectsAccordion">
        <p v-if="!subjects.length" class="text-center text-muted mt-4">No subjects created yet.</p>
        
        <div v-for="subject in subjects" :key="subject.id" class="accordion-item mb-3">
          <h2 class="accordion-header" :id="'headingSubject' + subject.id">
            <div class="d-flex align-items-center p-2">
              <button class="accordion-button collapsed flex-grow-1" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapseSubject' + subject.id" aria-expanded="false">
                {{ subject.name }}
              </button>
              <router-link :to="{ name: 'AdminEditSubject', params: { subjectId: subject.id } }" class="btn btn-sm btn-outline-primary ms-2">Edit</router-link>
              <form @submit.prevent="deleteSubjectHandler(subject)" class="d-inline ms-1">
                <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
              </form>
            </div>
          </h2>
          <div :id="'collapseSubject' + subject.id" class="accordion-collapse collapse" data-bs-parent="#subjectsAccordion">
            <div class="accordion-body">
              <p v-if="subject.description"><em>{{ subject.description }}</em></p>
              <hr>
              <h5 class="mt-3 ChapterHeadingsInsideAdminDashboardSubject">Chapters</h5>
              <ul v-if="subject.chapters && subject.chapters.length" class="list-unstyled">
                <li v-for="chapter in subject.chapters" :key="chapter.id" class="chapter-item-container">
                  <div class="chapter-item">
                    <span class="flex-grow-1 me-3">{{ chapter.name }}</span>
                    <div class="chapter-controls flex-shrink-0">
                      <button class="btn btn-sm btn-outline-info" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapseQuizzes' + chapter.id">
                        Quizzes <span class="badge bg-secondary">{{ chapter.quizzes?.length || 0 }}</span>
                      </button>
                      <router-link :to="{ name: 'AdminEditChapter', params: { chapterId: chapter.id } }" class="btn btn-sm btn-outline-primary">Edit</router-link>
                      <form @submit.prevent="deleteChapterHandler(chapter, subject)" class="d-inline ms-1">
                        <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                      </form>
                    </div>
                  </div>
                  
                  <div class="collapse quiz-list-nested mt-2" :id="'collapseQuizzes' + chapter.id">
                    <ul v-if="chapter.quizzes && chapter.quizzes.length" class="list-unstyled">
                        <li v-for="quiz in chapter.quizzes" :key="quiz.id" class="quiz-item">
                            <span>{{ quiz.title }} ({{ quiz.duration_minutes }} min) <span v-if="!quiz.is_active" class="badge bg-warning text-dark">Inactive</span></span>
                            <div class="quiz-controls">
                              <router-link :to="{ name: 'AdminManageQuestions', params: { quizId: quiz.id } }" class="btn btn-sm btn-outline-secondary">Questions</router-link>
                               <router-link :to="{ name: 'AdminEditQuiz', params: { quizId: quiz.id } }" class="btn btn-sm btn-outline-primary">Edit</router-link>
                               <form @submit.prevent="deleteQuizHandler(quiz, chapter)" class="d-inline ms-1">
                                <button type="submit" class="btn btn-sm btn-outline-danger">Del</button>
                               </form>
                            </div>
                        </li>
                    </ul>
                    <p v-else class="small ">No quizzes in this chapter.</p>
                    <router-link :to="{ name: 'AdminAddQuiz', query: { chapterId: chapter.id } }" class="btn btn-sm btn-success mt-2">+ Add Quiz</router-link>
                  </div>
                </li>
              </ul>
              <p v-else class="small">No chapters found. Add one below.</p>

              <form @submit.prevent="addChapterHandler(subject)" class="add-chapter-form row g-2 align-items-center mt-3">
                <div class="col-auto flex-grow-1">
                  <input type="text" v-model="newChapterNames[subject.id]" class="form-control form-control-sm" placeholder="New Chapter Name" required>
                </div>
                <div class="col-auto">
                  <button type="submit" class="btn btn-secondary btn-sm">Add Chapter</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import adminService from '@/services/adminService';

// Component State
const auth = useAuthStore();
const subjects = ref([]);
const loading = ref(true);
const error = ref('');

// Form State
const newSubject = reactive({ name: '', description: '' });
const addSubjectLoading = ref(false);
const addSubjectError = ref('');
const newChapterNames = reactive({}); // Holds input values for each "Add Chapter" form

onMounted(() => {
  fetchDashboardData();
});

// Fetches all data and assembles the nested structure needed by the template
async function fetchDashboardData() {
  loading.value = true;
  error.value = '';
  try {
    const [subjectsRes, chaptersRes, quizzesRes] = await Promise.all([
      adminService.getSubjects(),
      adminService.getChapters(),
      adminService.getAllQuizzes()
    ]);

    const allSubjects = subjectsRes.data.subjects || [];
    const allChapters = chaptersRes.data.chapters || [];
    const allQuizzes = quizzesRes.data.quizzes || [];

    const chapterMap = new Map(allChapters.map(ch => [ch.id, { ...ch, quizzes: [] }]));
    
    allQuizzes.forEach(quiz => {
      if (chapterMap.has(quiz.chapter_id)) {
        chapterMap.get(quiz.chapter_id).quizzes.push(quiz);
      }
    });

    allSubjects.forEach(sub => {
      sub.chapters = allChapters
        .filter(ch => ch.subject_id === sub.id)
        .map(ch => chapterMap.get(ch.id)); 
      newChapterNames[sub.id] = '';
    });

    subjects.value = allSubjects;

  } catch (err) {
    console.error("Error fetching dashboard data:", err);
    error.value = err.response?.data?.message || 'Failed to load dashboard data.';
  } finally {
    loading.value = false;
  }
}

// --- CRUD Handlers ---

async function addSubjectHandler() {
  addSubjectLoading.value = true;
  addSubjectError.value = '';
  try {
    const response = await adminService.addSubject(newSubject);
    const addedSubject = { ...response.data, chapters: [] };
    subjects.value.push(addedSubject);
    newChapterNames[addedSubject.id] = '';
    newSubject.name = '';
    newSubject.description = '';
  } catch (err) {
    addSubjectError.value = err.response?.data?.message || 'Failed to add subject.';
  } finally {
    addSubjectLoading.value = false;
  }
}

async function deleteSubjectHandler(subjectToDelete) {
  if (confirm(`Delete subject '${subjectToDelete.name}' and ALL its contents?`)) {
    try {
      await adminService.deleteSubject(subjectToDelete.id);
      subjects.value = subjects.value.filter(s => s.id !== subjectToDelete.id);
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete subject.');
    }
  }
}

async function addChapterHandler(parentSubject) {
  const chapterName = newChapterNames[parentSubject.id]?.trim();
  if (!chapterName) return;
  try {
    const response = await adminService.addChapter({ name: chapterName, subject_id: parentSubject.id });
    parentSubject.chapters.push({ ...response.data, quizzes: [] });
    newChapterNames[parentSubject.id] = '';
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to add chapter.');
  }
}

async function deleteChapterHandler(chapterToDelete, parentSubject) {
  if (confirm(`Delete chapter '${chapterToDelete.name}' and all its quizzes?`)) {
    try {
      await adminService.deleteChapter(chapterToDelete.id);
      parentSubject.chapters = parentSubject.chapters.filter(c => c.id !== chapterToDelete.id);
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete chapter.');
    }
  }
}

async function deleteQuizHandler(quizToDelete, parentChapter) {
  if (confirm(`Delete quiz '${quizToDelete.title}'?`)) {
    try {
      await adminService.deleteQuiz(quizToDelete.id);
      parentChapter.quizzes = parentChapter.quizzes.filter(q => q.id !== quizToDelete.id);
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete quiz.');
    }
  }
}

function featureNotImplemented(featureName) {
  alert(`${featureName} feature is not implemented yet. You need to create the component and add it to the router.`);
}
</script>

