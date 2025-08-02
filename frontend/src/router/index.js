// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth'; // Import Pinia store

// Import Views (using lazy loading)
const LoginPage = () => import('@/views/LoginPage.vue');
const UserDashboard = () => import('@/views/UserDashboard.vue'); 
const AdminDashboard = () => import('@/views/AdminDashboard.vue'); 
const UserSummaryPage = () => import('@/views/UserSummaryPage.vue'); 
const AdminSummaryPage = () => import('@/views/AdminSummaryPage.vue'); 
const AdminAllQuizzes = () => import('@/views/AdminAllQuizzes.vue'); 
const AdminSearchPage = () => import('@/views/AdminSearchPage.vue'); 
const AttendQuizPage = () => import('@/views/AttendQuizPage.vue'); 
const NotFoundPage = () => import('@/views/NotFoundPage.vue'); 
const AdminEditSubject = () => import('@/views/AdminEditSubject.vue');
const AdminEditChapter = () => import('@/views/AdminEditChapter.vue');
const AdminEditQuiz = () => import('@/views/AdminEditQuiz.vue');
const AdminManageQuestions = () => import('@/views/AdminManageQuestions.vue');
const AdminEditQuestion = () => import('@/views/AdminEditQuestion.vue');
const AdminAddQuiz = () => import('@/views/AdminAddQuiz.vue');
const AdminUserActivityPage = () => import('@/views/AdminUserActivityPage.vue');
// Add imports for other admin pages (quiz edit, question manage etc.) later

const routes = [

  {
    path: '/',
    name: 'Home',
    redirect: () => {
      
      const token = localStorage.getItem('authToken');
      if (token) {
        // If token exists, try going to the user dashboard.
        // The guard will verify token validity and check roles later.
        return { name: 'UserDashboard' };
      } else {
        // No token, must login.
        return { name: 'Login' };
      }
    },
  },
  {
    path: '/admin/quizzes/add',
    name: 'AdminAddQuiz',
    component: AdminAddQuiz,
    meta: { requiresAuth: true, roles: ['admin'] }
  },


  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true } 
  },
  // User Dashboard (requires auth)
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true } // Basic auth check
  },
  // User Summary (requires auth)
  {
    path: '/summary',
    name: 'UserSummary',
    component: UserSummaryPage,
    meta: { requiresAuth: true }
  },
  
   
  {
    path: '/attempt/:attemptId', 
    name: 'AttendQuiz',
    component: AttendQuizPage,
    props: true, 
    meta: { requiresAuth: true }
  },

  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin'] } 
  },
  // Admin Summary (requires auth + admin role)
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummaryPage,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
   // Admin All Quizzes (requires auth + admin role)
  {
    path: '/admin/quizzes',
    name: 'AdminAllQuizzes',
    component: AdminAllQuizzes,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/users/:userId/activity',
    name: 'AdminUserActivity',
    component: AdminUserActivityPage,
    props: true, 
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  // Admin Search (requires auth + admin role)
  {
    path: '/admin/search',
    name: 'AdminSearch',
    component: AdminSearchPage,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/quizzes/:quizId/edit',
    name: 'AdminEditQuiz',
    component: AdminEditQuiz,
    props: true, // Passes the ':quizId' as a prop
    meta: { requiresAuth: true, roles: ['admin'] }
  },

  {
    path: '/admin/subjects/:subjectId/edit',
    name: 'AdminEditSubject',
    component: AdminEditSubject,
    props: true, // This is important! It passes the ':subjectId' as a prop to the component
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/chapters/:chapterId/edit',
    name: 'AdminEditChapter',
    component: AdminEditChapter,
    props: true, // Passes the ':chapterId' from the URL as a prop
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/quizzes/:quizId/questions',
    name: 'AdminManageQuestions',
    component: AdminManageQuestions,
    props: true, // Passes the ':quizId' as a prop
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/questions/:questionId/edit',
    name: 'AdminEditQuestion',
    component: AdminEditQuestion,
    props: true, // Passes ':questionId' as a prop
    meta: { requiresAuth: true, roles: ['admin'] }
  },

  // Add other admin routes for editing subjects, chapters, quizzes, questions later

  // Catch all 404
   {
     path: '/:pathMatch(.*)*', // Matches everything not matched above
     name: 'NotFound',
     component: NotFoundPage
    }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Use history mode
  routes,
  linkActiveClass: 'active', // Optional: class for active router-links (matches Bootstrap)
});

// --- Navigation Guards (Keep as before - this logic is correct here) ---
router.beforeEach((to, from, next) => {
  // Get auth store instance inside the guard
  const auth = useAuthStore();

  // Attempt to check auth status silently on navigation if token exists but state might be lost
  if (!auth.isAuthenticated && localStorage.getItem('authToken')) {
      console.log("Guard: Rehydrating auth state from storage..."); // DEBUG
      auth.checkAuth(); // Try to rehydrate state from token
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);
  const requiredRoles = to.meta.roles; // Array of roles allowed, if specified

  // Use a local variable for isAuthenticated AFTER potential rehydration
  const isAuthenticated = auth.isAuthenticated;
  const userRoles = auth.user?.roles || []; // Use current user state from store

  console.log(`Guard Navigating to: ${to.path}, requiresAuth: ${requiresAuth}, requiresGuest: ${requiresGuest}, isAuthenticated: ${isAuthenticated}`); // Debugging

  if (requiresAuth && !isAuthenticated) {
    // Redirect to login if auth is required but user is not logged in
    console.log(`Guard: Redirecting to login (auth required, not authenticated)`);
    next({ name: 'Login', query: { redirect: to.fullPath } }); // Pass intended destination
  } else if (requiresGuest && isAuthenticated) {
    // Redirect away from guest pages (like login) if already logged in
     console.log(`Guard: Redirecting from guest page ${to.path} to dashboard`);
     next(auth.isAdmin ? { name: 'AdminDashboard' } : { name: 'UserDashboard' });
  } else if (requiresAuth && requiredRoles) {
     // Check roles if required
     const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));
     if (!hasRequiredRole) {
         console.log(`Guard: Redirecting due to insufficient roles for ${to.path}. Required: ${requiredRoles}, User has: ${userRoles}`);
         next({ name: 'UserDashboard' }); 
     } else {
         next(); // User has required role
     }
  }
  else {
    next();
  }
});


export default router;

