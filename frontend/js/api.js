/**
 * ProgressPro API Client
 * Manages JWT authentication lifecycle, token auto-refresh, and typed API calls
 * across all 26 endpoints.
 */

class ApiClient {
  constructor() {
    // Dynamic origin detection: If loaded from FastAPI /ui, use window.location.origin
    // If opened via file:// or custom dev server, fallback to default API port 8000
    if (window.location.protocol.startsWith('http') && window.location.port !== '') {
      this.baseUrl = window.location.origin;
    } else {
      this.baseUrl = 'http://127.0.0.1:8000';
    }
    this.apiPrefix = '/api/v1';
  }

  get accessToken() {
    return localStorage.getItem('progresspro_access_token');
  }

  set accessToken(token) {
    if (token) {
      localStorage.setItem('progresspro_access_token', token);
    } else {
      localStorage.removeItem('progresspro_access_token');
    }
  }

  get refreshToken() {
    return localStorage.getItem('progresspro_refresh_token');
  }

  set refreshToken(token) {
    if (token) {
      localStorage.setItem('progresspro_refresh_token', token);
    } else {
      localStorage.removeItem('progresspro_refresh_token');
    }
  }

  get userEmail() {
    return localStorage.getItem('progresspro_user_email');
  }

  set userEmail(email) {
    if (email) {
      localStorage.setItem('progresspro_user_email', email);
    } else {
      localStorage.removeItem('progresspro_user_email');
    }
  }

  isAuthenticated() {
    return !!this.accessToken;
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    this.userEmail = null;
  }

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    if (this.accessToken && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    try {
      let response = await fetch(url, { ...options, headers });

      // If token expired (401) and we have a refresh token, attempt transparent refresh once
      if (response.status === 401 && this.refreshToken && !options._isRetry) {
        const refreshed = await this.refreshTokens();
        if (refreshed) {
          options._isRetry = true;
          headers['Authorization'] = `Bearer ${this.accessToken}`;
          response = await fetch(url, { ...options, headers });
        } else {
          this.logout();
        }
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMessage = data?.error?.message || data?.detail || `API error (${response.status})`;
        const err = new Error(errorMessage);
        err.status = response.status;
        err.payload = data;
        throw err;
      }

      return data;
    } catch (error) {
      console.error(`[API ERROR] ${options.method || 'GET'} ${endpoint}:`, error);
      throw error;
    }
  }

  async refreshTokens() {
    try {
      const res = await fetch(`${this.baseUrl}${this.apiPrefix}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken })
      });
      if (!res.ok) return false;
      const data = await res.json();
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      return true;
    } catch {
      return false;
    }
  }

  // System & Health
  async getHealth() {
    return fetch(`${this.baseUrl}/health`).then(r => r.json());
  }

  // Authentication & Users
  async register(email, password, fullName = null) {
    return this.request(`${this.apiPrefix}/auth/register`, {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName })
    });
  }

  async login(email, password) {
    const data = await this.request(`${this.apiPrefix}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    this.userEmail = email;
    return data;
  }

  async getMe() {
    return this.request(`${this.apiPrefix}/users/me`);
  }

  async updateMe(data) {
    return this.request(`${this.apiPrefix}/users/me`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // Profile
  async getProfile() {
    const data = await this.request(`${this.apiPrefix}/profile`);
    if (data) {
      if (!data.birth_date && data.date_of_birth) data.birth_date = data.date_of_birth;
      if (!data.weight_kg && data.target_weight_kg) data.weight_kg = data.target_weight_kg;
    }
    return data;
  }

  async createProfile(data) {
    const payload = { ...data };
    if (payload.birth_date && !payload.date_of_birth) payload.date_of_birth = payload.birth_date;
    if (payload.weight_kg !== undefined && payload.target_weight_kg === undefined) payload.target_weight_kg = payload.weight_kg;
    return this.request(`${this.apiPrefix}/profile`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async updateProfile(data) {
    const payload = { ...data };
    if (payload.birth_date && !payload.date_of_birth) payload.date_of_birth = payload.birth_date;
    if (payload.weight_kg !== undefined && payload.target_weight_kg === undefined) payload.target_weight_kg = payload.weight_kg;
    return this.request(`${this.apiPrefix}/profile`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  }

  // Exercises
  async getExercises(params = {}) {
    const query = new URLSearchParams(params).toString();
    const endpoint = query ? `${this.apiPrefix}/exercises?${query}` : `${this.apiPrefix}/exercises`;
    return this.request(endpoint);
  }

  async createExercise(data) {
    return this.request(`${this.apiPrefix}/exercises`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Workouts
  async getWorkouts(params = {}) {
    const query = new URLSearchParams(params).toString();
    const endpoint = query ? `${this.apiPrefix}/workouts?${query}` : `${this.apiPrefix}/workouts`;
    return this.request(endpoint);
  }

  async getWorkout(id) {
    return this.request(`${this.apiPrefix}/workouts/${id}`);
  }

  async createWorkout(data) {
    const payload = { ...data };
    if (!payload.title) {
      payload.title = payload.notes ? payload.notes.slice(0, 100) : `Workout Session - ${payload.workout_date || new Date().toISOString().split('T')[0]}`;
    }
    if (payload.exercises && !payload.workout_exercises) {
      payload.workout_exercises = payload.exercises.map((ex, idx) => ({
        exercise_id: ex.exercise_id,
        order: ex.order || ex.order_in_workout || (idx + 1),
        notes: ex.notes || null,
        exercise_sets: (ex.exercise_sets || ex.sets || []).map((s, sIdx) => ({
          set_number: s.set_number || (sIdx + 1),
          set_type: s.set_type || 'normal',
          weight_kg: s.weight_kg ?? 0,
          reps: s.reps ?? 0,
          rpe: s.rpe ?? null,
          is_completed: s.is_completed !== undefined ? s.is_completed : true
        }))
      }));
      delete payload.exercises;
    }
    return this.request(`${this.apiPrefix}/workouts`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async deleteWorkout(id) {
    return this.request(`${this.apiPrefix}/workouts/${id}`, {
      method: 'DELETE'
    });
  }

  // Daily Tracking
  async getWeightRecords(limit = 14) {
    return this.request(`${this.apiPrefix}/tracking/weight?limit=${limit}`);
  }

  async logWeight(data) {
    const payload = { ...data };
    if (payload.body_fat_pct !== undefined && payload.body_fat_percentage === undefined) {
      payload.body_fat_percentage = payload.body_fat_pct;
      delete payload.body_fat_pct;
    }
    return this.request(`${this.apiPrefix}/tracking/weight`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getSleepRecords(limit = 14) {
    return this.request(`${this.apiPrefix}/tracking/sleep?limit=${limit}`);
  }

  async logSleep(data) {
    const payload = { ...data };
    if (payload.sleep_hours !== undefined && payload.sleep_duration_hours === undefined) {
      payload.sleep_duration_hours = payload.sleep_hours;
      delete payload.sleep_hours;
    }
    if (payload.sleep_quality !== undefined && payload.quality_score === undefined) {
      payload.quality_score = payload.sleep_quality;
      delete payload.sleep_quality;
    }
    return this.request(`${this.apiPrefix}/tracking/sleep`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getNutritionRecords(limit = 14) {
    return this.request(`${this.apiPrefix}/tracking/nutrition?limit=${limit}`);
  }

  async logNutrition(data) {
    const payload = { ...data };
    if (payload.protein_g !== undefined && payload.protein === undefined) {
      payload.protein = payload.protein_g;
      delete payload.protein_g;
    }
    if (payload.carbs_g !== undefined && payload.carbs === undefined) {
      payload.carbs = payload.carbs_g;
      delete payload.carbs_g;
    }
    if (payload.fat_g !== undefined && payload.fats === undefined) {
      payload.fats = payload.fat_g;
      delete payload.fat_g;
    }
    if (payload.water_liters !== undefined && payload.water === undefined) {
      payload.water = payload.water_liters;
      delete payload.water_liters;
    }
    if (payload.carbs === null || payload.carbs === undefined) payload.carbs = 0;
    if (payload.fats === null || payload.fats === undefined) payload.fats = 0;
    return this.request(`${this.apiPrefix}/tracking/nutrition`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Analytics Subsystem
  async getVolumeAnalytics() {
    return this.request(`${this.apiPrefix}/analytics/volume`);
  }

  async getStrengthAnalytics(exerciseId) {
    return this.request(`${this.apiPrefix}/analytics/strength/${exerciseId}`);
  }

  async getConsistencyAnalytics() {
    return this.request(`${this.apiPrefix}/analytics/consistency`);
  }

  async getOverloadAnalytics(exerciseId) {
    return this.request(`${this.apiPrefix}/analytics/progressive-overload/${exerciseId}`);
  }

  async getRecoveryAnalytics() {
    return this.request(`${this.apiPrefix}/analytics/recovery`);
  }

  async getProgressScore() {
    return this.request(`${this.apiPrefix}/analytics/progress-score`);
  }

  // Recommendation Engine
  async getFitnessRecommendations() {
    return this.request(`${this.apiPrefix}/recommendations/fitness`);
  }

  async getNutritionRecommendations() {
    return this.request(`${this.apiPrefix}/recommendations/nutrition`);
  }

  async getComprehensiveReport() {
    return this.request(`${this.apiPrefix}/recommendations/report`);
  }
}

// Global API instance
window.api = new ApiClient();
