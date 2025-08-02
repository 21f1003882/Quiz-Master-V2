<template>
    <div>
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      
      <div v-else>
        <h1 class="mb-4">Edit Subject</h1>
        <h5 class="mb-3 text-muted">Editing: {{ initialSubjectName }}</h5>
  
        <form @submit.prevent="handleUpdate">
          <div class="mb-3">
            <label for="subjectName" class="form-label">Subject Name</label>
            <input type="text" id="subjectName" class="form-control" v-model="subject.name" required>
          </div>
  
          <div class="mb-3">
            <label for="subjectDescription" class="form-label">Description</label>
            <textarea id="subjectDescription" class="form-control" v-model="subject.description" rows="3"></textarea>
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
    subjectId: {
      type: String,
      required: true
    }
  });
  
  const router = useRouter();
  
  // State for fetching initial data
  const loading = ref(true);
  const error = ref('');
  const initialSubjectName = ref('');
  
  // State for the form
  const subject = reactive({ name: '', description: '' });
  const isSubmitting = ref(false);
  const updateError = ref('');
  
  // Fetch subject data when the component is first mounted
  onMounted(async () => {
    try {
      const response = await adminService.getSubject(props.subjectId);
      // Populate the form with the fetched data
      subject.name = response.data.name;
      subject.description = response.data.description;
      initialSubjectName.value = response.data.name; // Store original name for display
    } catch (err) {
      console.error('Failed to fetch subject:', err);
      error.value = err.response?.data?.message || 'Subject not found.';
    } finally {
      loading.value = false;
    }
  });
  
  // Handle the form submission
  const handleUpdate = async () => {
    isSubmitting.value = true;
    updateError.value = '';
    try {
      await adminService.updateSubject(props.subjectId, subject);
      // On success, navigate back to the dashboard
      router.push({ name: 'AdminDashboard' });
      // You could implement a flash message system here later
      alert('Subject updated successfully!');
    } catch (err) {
      console.error('Failed to update subject:', err);
      updateError.value = err.response?.data?.message || 'An error occurred while updating.';
    } finally {
      isSubmitting.value = false;
    }
  };
  </script>
  
