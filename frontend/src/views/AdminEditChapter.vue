<template>
    <div>
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else>
        <h1 class="mb-4">Edit Chapter</h1>
        <h5 class="mb-3 text-muted">Editing: {{ initialChapterName }}</h5>
  
        <form @submit.prevent="handleUpdate">
          <div class="mb-3">
            <label for="chapterName" class="form-label">Chapter Name</label>
            <input type="text" id="chapterName" class="form-control" v-model="chapter.name" required>
          </div>
  
          <div v-if="updateError" class="alert alert-danger mt-3">{{ updateError }}</div>
  
          <div class="mt-4">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>
            <router-link :to="{ name: 'AdminDashboard' }" class="btn btn-secondary ms-2">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import adminService from '@/services/adminService';
  
  const props = defineProps({
    chapterId: {
      type: String,
      required: true
    }
  });
  
  const router = useRouter();
  
  // State for fetching initial data
  const loading = ref(true);
  const error = ref('');
  const initialChapterName = ref('');
  
  // State for the form
  const chapter = reactive({ name: '' });
  const isSubmitting = ref(false);
  const updateError = ref('');
  
  // Fetch chapter data when the component is first mounted
  onMounted(async () => {
    try {
      const response = await adminService.getChapter(props.chapterId);
      chapter.name = response.data.name;
      initialChapterName.value = response.data.name;
    } catch (err) {
      console.error('Failed to fetch chapter:', err);
      error.value = err.response?.data?.message || 'Chapter not found.';
    } finally {
      loading.value = false;
    }
  });
  
  // Handle the form submission
  const handleUpdate = async () => {
    isSubmitting.value = true;
    updateError.value = '';
    try {
      await adminService.updateChapter(props.chapterId, chapter);
      router.push({ name: 'AdminDashboard' });
      alert('Chapter updated successfully!');
    } catch (err) {
      console.error('Failed to update chapter:', err);
      updateError.value = err.response?.data?.message || 'An error occurred while updating.';
    } finally {
      isSubmitting.value = false;
    }
  };
  </script>
  
