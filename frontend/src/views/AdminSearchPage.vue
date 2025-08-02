<template>
    <div>
      <h1 class="adminHeading mb-4">Search</h1>
  
      <!-- Search Bar -->
      <div class="search-bar-container">
        <form @submit.prevent="executeSearch" class="search-form position-relative">
          <input
            type="search"
            v-model="searchQuery"
            class="form-control search-input"
            placeholder="Search Users, Subjects, Quizzes..."
            aria-label="Search"
          />
          <button class="search-button" type="submit" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
            </svg>
          </button>
        </form>
      </div>
  
      <!-- Error Display -->
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
  
      <!-- Results Display -->
      <div v-if="searched">
        <h2 class="mb-4">Search Results for "{{ initialQuery }}"</h2>
  
        <!-- Users -->
        <div class="results-section">
          <h4>Users Found ({{ results.users.length }})</h4>
          <ul v-if="results.users.length" class="list-group list-group-flush">
            <li v-for="user in results.users" :key="user.id" class="list-group-item">
              <span>{{ user.username }} ({{ user.email }})</span>
            </li>
          </ul>
          <p v-else class="text-muted">No users found matching your query.</p>
        </div>
  
        <!-- Subjects -->
        <div class="results-section">
          <h4>Subjects Found ({{ results.subjects.length }})</h4>
          <ul v-if="results.subjects.length" class="list-group list-group-flush">
            <li v-for="subject in results.subjects" :key="subject.id" class="list-group-item">
              <span>{{ subject.name }}</span>
              <button @click="featureNotImplemented('Edit Subject')" class="btn btn-sm btn-outline-secondary">Edit</button>
            </li>
          </ul>
          <p v-else class="text-muted">No subjects found matching your query.</p>
        </div>
  
        <!-- Quizzes -->
        <div class="results-section">
          <h4>Quizzes Found ({{ results.quizzes.length }})</h4>
          <ul v-if="results.quizzes.length" class="list-group list-group-flush">
            <li v-for="quiz in results.quizzes" :key="quiz.id" class="list-group-item">
              <span>{{ quiz.title }} <small class="text-muted">({{ quiz.chapter_name }} / {{ quiz.subject_name }})</small></span>
              <span>
                <button @click="featureNotImplemented('Manage Questions')" class="btn btn-sm btn-outline-secondary">Questions</button>
                <button @click="featureNotImplemented('Edit Quiz')" class="btn btn-sm btn-outline-primary ms-1">Edit</button>
              </span>
            </li>
          </ul>
          <p v-else class="text-muted">No quizzes found matching your query.</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import adminService from '@/services/adminService';
  
  const route = useRoute();
  const router = useRouter();
  
  const searchQuery = ref('');
  const initialQuery = ref(''); // To display in the "Results for..." heading
  const results = reactive({ users: [], subjects: [], quizzes: [] });
  const loading = ref(false);
  const error = ref('');
  const searched = ref(false); // To know if a search has been performed
  
  // This function performs the search by updating the URL query
  const executeSearch = async () => {
    if (!searchQuery.value.trim()) return;
    router.push({ query: { q: searchQuery.value } });
  };
  
  // This function fetches data from the API based on the URL query
  const fetchResults = async (query) => {
    if (!query) {
      Object.assign(results, { users: [], subjects: [], quizzes: [] });
      searched.value = false;
      return;
    }
    
    loading.value = true;
    error.value = '';
    searched.value = true;
    initialQuery.value = query;
  
    try {
      const response = await adminService.search(query);
      Object.assign(results, response.data);
    } catch (err) {
      console.error('Search failed:', err);
      error.value = err.response?.data?.message || 'Failed to perform search.';
    } finally {
      loading.value = false;
    }
  };
  
  // Watch for changes in the URL query parameter 'q'.
  // This allows the page to be bookmarkable and triggers a search on load/navigation.
  watch(() => route.query.q, (newQuery) => {
    searchQuery.value = newQuery || '';
    fetchResults(newQuery);
  }, { immediate: true }); // 'immediate: true' runs the watcher when the component is first created
  
  function featureNotImplemented(featureName) {
    alert(`${featureName} feature is not implemented yet.`);
  }
  </script>
  
  