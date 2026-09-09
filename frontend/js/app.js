/**
 * ProgressPro Main Application Controller
 * Handles UI events, tab routing, modals, dynamic charting, and API integration.
 */

document.addEventListener('DOMContentLoaded', () => {
  // State
  let exercisesList = [];
  let currentTab = 'overview';
  let isRegisterMode = false;

  // UI Element References
  const toastContainer = document.getElementById('toast-container');
  const healthBadge = document.getElementById('health-badge');
  const healthDot = document.getElementById('health-dot');
  const healthStatusText = document.getElementById('health-status-text');
  const userDisplayName = document.getElementById('user-display-name');
  const userAvatar = document.getElementById('user-avatar');
  const demoBanner = document.getElementById('demo-banner');
  const quickDemoBtn = document.getElementById('quick-demo-btn');
  const btnDemoAuthFill = document.getElementById('btn-demo-auth-fill');
  const authActionBtn = document.getElementById('auth-action-btn');

  // Modals
  const modalWorkout = document.getElementById('modal-workout');
  const modalAuth = document.getElementById('modal-auth');

  // ==========================================================================
  // Toast Notifications
  // ==========================================================================
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // ==========================================================================
  // Health Check & Auth Status
  // ==========================================================================
  async function checkApiHealth() {
    try {
      const data = await window.api.getHealth();
      if (data.status === 'healthy') {
        healthDot.style.background = '#10b981';
        healthStatusText.textContent = data.database === 'connected' ? 'API & DB Live' : 'API Live (No DB)';
      }
    } catch {
      healthDot.style.background = '#f43f5e';
      healthStatusText.textContent = 'Offline';
    }
  }

  function updateAuthUI() {
    if (window.api.isAuthenticated()) {
      const email = window.api.userEmail || 'Athlete';
      userDisplayName.textContent = email.split('@')[0];
      userAvatar.textContent = email[0].toUpperCase();
      demoBanner.style.display = 'none';
      authActionBtn.textContent = 'Sign Out';
    } else {
      userDisplayName.textContent = 'Guest';
      userAvatar.textContent = '?';
      demoBanner.style.display = 'flex';
      authActionBtn.textContent = 'Sign In';
    }
  }

  // ==========================================================================
  // Tab Routing
  // ==========================================================================
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;
      switchTab(tabName);
    });
  });

  function switchTab(tabName) {
    currentTab = tabName;
    tabButtons.forEach(b => b.classList.toggle('active', b.dataset.tab === tabName));
    document.querySelectorAll('.tab-view').forEach(view => {
      view.classList.toggle('active', view.id === `view-${tabName}`);
    });

    // Refresh tab-specific data
    if (tabName === 'overview') loadOverviewData();
    else if (tabName === 'workouts') loadWorkoutsData();
    else if (tabName === 'tracking') loadTrackingData();
    else if (tabName === 'analytics') loadAnalyticsData();
    else if (tabName === 'recommendations') loadRecommendationsData();
    else if (tabName === 'profile') loadProfileData();
  }

  document.getElementById('view-all-recs-btn')?.addEventListener('click', () => switchTab('recommendations'));
  document.getElementById('brand-link')?.addEventListener('click', (e) => { e.preventDefault(); switchTab('overview'); });

  // ==========================================================================
  // Exercises Catalog Preload
  // ==========================================================================
  async function loadExercisesCatalog() {
    try {
      const data = await window.api.getExercises({ limit: 100 });
      exercisesList = Array.isArray(data) ? data : (data.items || []);
      populateStrengthSelector();
    } catch (err) {
      console.warn('Could not preload exercises catalog:', err);
    }
  }

  function populateStrengthSelector() {
    const selector = document.getElementById('select-strength-exercise');
    if (!selector) return;
    selector.innerHTML = '';
    exercisesList.forEach(ex => {
      const opt = document.createElement('option');
      opt.value = ex.id;
      const muscle = ex.primary_muscle_group || ex.target_muscle_group || 'General';
      opt.textContent = `${ex.name} (${muscle})`;
      selector.appendChild(opt);
    });
  }

  // ==========================================================================
  // 1. Overview Data Loader
  // ==========================================================================
  async function loadOverviewData() {
    if (!window.api.isAuthenticated()) return;

    try {
      // 1. Composite Progress Score
      const scoreData = await window.api.getProgressScore().catch(() => null);
      if (scoreData) {
        const finalScore = scoreData.score ?? scoreData.overall_score ?? 0;
        document.getElementById('stat-progress-score').textContent = Math.round(finalScore);
        document.getElementById('stat-progress-grade').textContent = `Rating: ${scoreData.rating || 'N/A'}`;

        const scoreCanvas = document.getElementById('overview-score-canvas');
        if (scoreCanvas) {
          window.ProgressCharts.drawRadialProgress(scoreCanvas, finalScore, scoreData.rating || 'PROGRESS');
        }

        // Pillar breakdown
        const pillarContainer = document.getElementById('pillar-breakdown');
        const pillars = scoreData.pillars ?? scoreData.pillar_breakdown ?? {};
        if (pillarContainer && Object.keys(pillars).length > 0) {
          pillarContainer.innerHTML = Object.entries(pillars).map(([pillar, val]) => {
            const cleanName = pillar.replace('_score', '').replace('_adherence', '');
            return `
            <div style="background: rgba(255,255,255,0.03); padding: 0.4rem 0.65rem; border-radius: 6px; border: 1px solid var(--border-subtle);">
              <div style="color: var(--text-muted); font-size: 0.68rem; text-transform: capitalize;">${cleanName}</div>
              <div style="font-weight: 700; color: #00f2fe; font-family: var(--font-mono);">${Math.round(val)}%</div>
            </div>`;
          }).join('');
        }
      }

      // 2. Weekly Consistency & Streak
      const consData = await window.api.getConsistencyAnalytics().catch(() => null);
      if (consData) {
        const freq = consData.actual_frequency_per_week ?? consData.average_weekly_frequency ?? 0;
        const streak = consData.current_active_streak_weeks ?? consData.current_streak_weeks ?? 0;
        document.getElementById('stat-frequency').textContent = `${typeof freq === 'number' ? freq.toFixed(1) : freq} d/wk`;
        document.getElementById('stat-streak').textContent = `Active streak: ${streak} wks`;
      }

      // 3. Sleep Recovery
      const recData = await window.api.getRecoveryAnalytics().catch(() => null);
      if (recData) {
        document.getElementById('stat-recovery-score').textContent = `${Math.round(recData.recovery_score || 0)}%`;
        const avgHours = recData.rolling_average_sleep_hours ?? recData.average_sleep_hours;
        const avgSleep = typeof avgHours === 'number' || typeof avgHours === 'string' ? parseFloat(avgHours).toFixed(1) : '--';
        document.getElementById('stat-sleep-avg').textContent = `7-day avg: ${avgSleep}h`;
      }

      // 4. Volume Tonnage
      const volData = await window.api.getVolumeAnalytics().catch(() => null);
      if (volData) {
        const totalTonnage = volData.total_tonnage_kg ?? (volData.weekly_breakdown?.reduce((sum, w) => sum + (w.total_tonnage || 0), 0) || 0);
        const totalSets = (volData.muscle_group_breakdown || []).reduce((sum, m) => sum + (m.effective_working_sets || 0), 0) || (volData.weekly_breakdown?.reduce((sum, w) => sum + (w.total_sets || 0), 0) || 0);
        document.getElementById('stat-tonnage').textContent = `${Math.round(totalTonnage).toLocaleString()} kg`;
        document.getElementById('stat-sets-count').textContent = `Total Sets: ${totalSets}`;
      }

      // 5. Diagnostic Alerts Banner
      const alertsContainer = document.getElementById('overview-alerts-container');
      const fitRecs = await window.api.getFitnessRecommendations().catch(() => []);
      const nutRecs = await window.api.getNutritionRecommendations().catch(() => []);
      const fitList = Array.isArray(fitRecs) ? fitRecs : (fitRecs.recommendations || []);
      const nutList = Array.isArray(nutRecs) ? nutRecs : (nutRecs.recommendations || []);
      const allRecs = [...fitList, ...nutList];

      if (allRecs.length === 0) {
        alertsContainer.innerHTML = `
          <div class="alert-banner alert-info">
            <span class="alert-icon">✓</span>
            <div>
              <div class="alert-title">Optimal Progress Detected</div>
              <div class="alert-desc">All training volume, overload progression, and nutrition targets are within recommended sports-science parameters.</div>
            </div>
          </div>`;
      } else {
        alertsContainer.innerHTML = allRecs.slice(0, 3).map(rec => {
          const sev = rec.severity || rec.priority || 'INFO';
          const isCrit = sev === 'CRITICAL' || sev === 'ACTION_REQUIRED';
          const typeClass = isCrit ? 'alert-critical' : sev === 'WARNING' ? 'alert-warning' : 'alert-info';
          const icon = isCrit ? '⚠️' : sev === 'WARNING' ? '⚡' : 'ℹ️';
          const ruleId = rec.rule_id || rec.rule_code || 'RULE';
          const title = rec.title || rec.actionable_guidance || rec.actionable_recommendation || '';
          const rationale = rec.rationale || rec.trigger_reason || '';
          return `
            <div class="alert-banner ${typeClass}">
              <span class="alert-icon">${icon}</span>
              <div>
                <div class="alert-title">[${ruleId}] ${title}</div>
                <div class="alert-desc">${rationale}</div>
              </div>
            </div>`;
        }).join('');
      }

      // 6. Recent Workouts Mini List
      const workoutsData = await window.api.getWorkouts({ limit: 3 }).catch(() => ([]));
      const workoutList = Array.isArray(workoutsData) ? workoutsData : (workoutsData.items || []);
      const recentContainer = document.getElementById('overview-recent-workouts');
      if (workoutList.length > 0) {
        recentContainer.innerHTML = workoutList.slice(0, 3).map(w => {
          const exercises = w.workout_exercises || w.exercises || [];
          let volLoad = w.total_volume_load || 0;
          if (!volLoad) {
            exercises.forEach(ex => {
              const sets = ex.exercise_sets || ex.sets || [];
              sets.forEach(s => { volLoad += (Number(s.weight_kg || 0) * Number(s.reps || 0)); });
            });
          }
          return `
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem; background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: 8px; margin-bottom: 0.5rem;">
            <div>
              <div style="font-weight: 700; font-size: 0.95rem;">${w.title || 'Workout Session'} &bull; ${w.workout_date} (${w.duration_minutes || 60}m)</div>
              <div style="color: var(--text-muted); font-size: 0.8rem;">${w.notes || 'Training Session'} &bull; ${exercises.length} Exercises</div>
            </div>
            <div style="text-align: right;">
              <span style="color: var(--accent-cyan); font-weight: 700; font-family: var(--font-mono);">${Math.round(volLoad).toLocaleString()} kg</span>
              <div style="font-size: 0.75rem; color: var(--text-muted);">Total Tonnage</div>
            </div>
          </div>`;
        }).join('');
      } else {
        recentContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">No workouts logged yet. Click "Log New Workout" to begin.</p>';
      }
    } catch (err) {
      console.error('Error loading overview data:', err);
    }
  }

  // ==========================================================================
  // 2. Workouts Data Loader & Session Cards
  // ==========================================================================
  async function loadWorkoutsData() {
    if (!window.api.isAuthenticated()) return;
    const container = document.getElementById('workouts-list-container');
    container.innerHTML = '<p style="color: var(--text-muted);">Fetching workout logs...</p>';

    try {
      const data = await window.api.getWorkouts({ limit: 20 });
      const workoutList = Array.isArray(data) ? data : (data.items || []);
      if (!workoutList || workoutList.length === 0) {
        container.innerHTML = `
          <div class="glass-card" style="text-align: center; padding: 3rem;">
            <p style="color: var(--text-muted); margin-bottom: 1rem;">No workout sessions recorded yet.</p>
            <button class="btn btn-primary" id="btn-empty-log-workout">Log Your First Workout</button>
          </div>`;
        document.getElementById('btn-empty-log-workout')?.addEventListener('click', openWorkoutModal);
        return;
      }

      container.innerHTML = workoutList.map(w => {
        const exercises = w.workout_exercises || w.exercises || [];
        let volLoad = w.total_volume_load || 0;
        if (!volLoad) {
          exercises.forEach(ex => {
            const sets = ex.exercise_sets || ex.sets || [];
            sets.forEach(s => { volLoad += (Number(s.weight_kg || 0) * Number(s.reps || 0)); });
          });
        }

        return `
        <div class="glass-card" style="margin-bottom: 1.25rem;">
          <div class="card-header" style="margin-bottom: 0.75rem;">
            <div>
              <h3 class="card-title" style="font-size: 1.15rem;">🏋️ ${w.title || 'Workout Session'} &bull; ${w.workout_date} (${w.duration_minutes || 60}m)</h3>
              <div class="card-subtitle">${w.notes || 'Standard Strength Session'}</div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
              <div style="text-align: right;">
                <div style="color: var(--accent-cyan); font-weight: 800; font-family: var(--font-mono); font-size: 1.15rem;">
                  ${Math.round(volLoad).toLocaleString()} kg
                </div>
                <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Volume Load</div>
              </div>
              <button class="btn btn-danger btn-sm btn-delete-workout" data-id="${w.id}">Delete</button>
            </div>
          </div>

          <!-- Exercises Breakdown -->
          <div style="display: flex; flex-direction: column; gap: 0.65rem;">
            ${exercises.map(ex => {
              const exName = ex.exercise?.name || ex.exercise_name || `Exercise #${ex.exercise_id}`;
              const sets = ex.exercise_sets || ex.sets || [];
              return `
              <div style="background: rgba(255,255,255,0.02); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid var(--border-subtle);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                  <strong style="color: #f8fafc; font-size: 0.92rem;">${exName}</strong>
                  <span style="color: var(--text-secondary); font-size: 0.8rem; font-family: var(--font-mono);">${sets.length} sets</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                  ${sets.map(s => `
                    <span style="background: rgba(0,242,254,0.08); border: 1px solid rgba(0,242,254,0.2); padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.78rem; font-family: var(--font-mono); color: #7dd3fc;">
                      Set ${s.set_number}: <strong>${s.weight_kg}kg</strong> × <strong>${s.reps}</strong> ${s.rpe ? `(RPE ${s.rpe})` : ''}
                    </span>
                  `).join('')}
                </div>
              </div>`;
            }).join('')}
          </div>
        </div>`;
      }).join('');

      // Attach delete listeners
      container.querySelectorAll('.btn-delete-workout').forEach(btn => {
        btn.addEventListener('click', async () => {
          if (confirm('Are you sure you want to delete this workout session?')) {
            try {
              await window.api.deleteWorkout(btn.dataset.id);
              showToast('Workout deleted successfully', 'success');
              loadWorkoutsData();
            } catch (err) {
              showToast(err.message, 'error');
            }
          }
        });
      });
    } catch (err) {
      container.innerHTML = `<p style="color: var(--accent-rose);">Failed to load workouts: ${err.message}</p>`;
    }
  }

  // ==========================================================================
  // 3. Daily Tracking Data & Forms
  // ==========================================================================
  function setTodayDateInputs() {
    const today = new Date().toISOString().split('T')[0];
    ['input-weight-date', 'input-sleep-date', 'input-nutrition-date', 'workout-input-date'].forEach(id => {
      const el = document.getElementById(id);
      if (el && !el.value) el.value = today;
    });
  }

  async function loadTrackingData() {
    if (!window.api.isAuthenticated()) return;
    setTodayDateInputs();

    // Load recent weight
    try {
      const wData = await window.api.getWeightRecords(5);
      const wList = document.getElementById('weight-history-list');
      const wItems = Array.isArray(wData) ? wData : (wData.items || []);
      if (wList && wItems.length > 0) {
        wList.innerHTML = `
          <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase;">Recent Logs</div>
          ${wItems.map(r => {
            const fat = r.body_fat_percentage ?? r.body_fat_pct;
            return `
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; padding: 0.35rem 0; border-bottom: 1px solid var(--border-subtle);">
              <span>${r.recorded_date}</span>
              <strong style="color: var(--accent-cyan); font-family: var(--font-mono);">${r.weight_kg} kg ${fat ? `(${fat}%)` : ''}</strong>
            </div>
            `;
          }).join('')}
        `;
      }
    } catch {}

    // Load recent sleep
    try {
      const sData = await window.api.getSleepRecords(5);
      const sList = document.getElementById('sleep-history-list');
      const sItems = Array.isArray(sData) ? sData : (sData.items || []);
      if (sList && sItems.length > 0) {
        sList.innerHTML = `
          <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase;">Recent Logs</div>
          ${sItems.map(r => {
            const hours = r.sleep_duration_hours ?? r.sleep_hours ?? 0;
            const quality = r.quality_score ?? r.sleep_quality ?? '-';
            return `
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; padding: 0.35rem 0; border-bottom: 1px solid var(--border-subtle);">
              <span>${r.recorded_date}</span>
              <strong style="color: var(--accent-violet); font-family: var(--font-mono);">${hours} hrs (Quality: ${quality}/5)</strong>
            </div>
            `;
          }).join('')}
        `;
      }
    } catch {}

    // Load recent nutrition
    try {
      const nData = await window.api.getNutritionRecords(5);
      const nList = document.getElementById('nutrition-history-list');
      const nItems = Array.isArray(nData) ? nData : (nData.items || []);
      if (nList && nItems.length > 0) {
        nList.innerHTML = `
          <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase;">Recent Logs</div>
          ${nItems.map(r => {
            const protein = r.protein ?? r.protein_g ?? 0;
            return `
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; padding: 0.35rem 0; border-bottom: 1px solid var(--border-subtle);">
              <span>${r.recorded_date}</span>
              <strong style="color: var(--accent-emerald); font-family: var(--font-mono);">${r.calories} kcal (P: ${protein}g)</strong>
            </div>
            `;
          }).join('')}
        `;
      }
    } catch {}
  }

  // Weight Form Submit
  document.getElementById('form-log-weight')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await window.api.logWeight({
        recorded_date: document.getElementById('input-weight-date').value,
        weight_kg: parseFloat(document.getElementById('input-weight-val').value),
        body_fat_percentage: document.getElementById('input-fat-val').value ? parseFloat(document.getElementById('input-fat-val').value) : null
      });
      showToast('Weight record saved', 'success');
      loadTrackingData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Sleep Form Submit
  document.getElementById('form-log-sleep')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await window.api.logSleep({
        recorded_date: document.getElementById('input-sleep-date').value,
        sleep_duration_hours: parseFloat(document.getElementById('input-sleep-hours').value),
        quality_score: parseInt(document.getElementById('input-sleep-quality').value),
        resting_heart_rate: document.getElementById('input-resting-hr').value ? parseInt(document.getElementById('input-resting-hr').value) : null
      });
      showToast('Sleep record saved', 'success');
      loadTrackingData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Nutrition Form Submit
  document.getElementById('form-log-nutrition')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await window.api.logNutrition({
        recorded_date: document.getElementById('input-nutrition-date').value,
        calories: parseInt(document.getElementById('input-calories').value),
        protein: parseFloat(document.getElementById('input-protein').value),
        carbs: document.getElementById('input-carbs').value ? parseFloat(document.getElementById('input-carbs').value) : 0,
        fats: document.getElementById('input-fats').value ? parseFloat(document.getElementById('input-fats').value) : 0,
        water: document.getElementById('input-water').value ? parseFloat(document.getElementById('input-water').value) : null
      });
      showToast('Nutrition record saved', 'success');
      loadTrackingData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // ==========================================================================
  // 4. Analytics Data & Dynamic Chart Rendering
  // ==========================================================================
  async function loadAnalyticsData() {
    if (!window.api.isAuthenticated()) return;

    if (exercisesList.length === 0) {
      await loadExercisesCatalog();
    }

    // 1. Volume Landmarks
    try {
      const volData = await window.api.getVolumeAnalytics();
      const canvas = document.getElementById('volume-landmarks-canvas');
      if (canvas) {
        const muscleSummary = volData.muscle_group_summary || {};
        if (volData.muscle_group_breakdown && Object.keys(muscleSummary).length === 0) {
          volData.muscle_group_breakdown.forEach(m => {
            muscleSummary[m.muscle_group] = m.effective_working_sets;
          });
        }
        window.ProgressCharts.drawVolumeLandmarksChart(canvas, muscleSummary);
      }
    } catch (err) {
      console.warn('Volume landmarks chart error:', err);
    }

    // 2. Strength Curve
    const selectExercise = document.getElementById('select-strength-exercise');
    if (selectExercise && selectExercise.value) {
      loadExerciseStrength(selectExercise.value);
    } else if (selectExercise && exercisesList.length > 0) {
      selectExercise.value = exercisesList[0].id;
      loadExerciseStrength(exercisesList[0].id);
    }

    // 3. Recovery Diagnostics
    try {
      const recData = await window.api.getRecoveryAnalytics();
      const recContainer = document.getElementById('recovery-diagnostic-container');
      if (recContainer) {
        const avgSleep = recData.rolling_average_sleep_hours ?? recData.average_sleep_hours ?? 0;
        const sleepDebt = recData.accumulated_sleep_debt_hours ?? recData.sleep_debt_hours ?? 0;
        recContainer.innerHTML = `
          <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
            <div>
              <div class="stat-label">7-Day Sleep Average</div>
              <div class="stat-value" style="font-size: 1.5rem; color: var(--accent-violet);">${parseFloat(avgSleep).toFixed(1)} hrs</div>
            </div>
            <div>
              <div class="stat-label">Accumulated Sleep Debt</div>
              <div class="stat-value" style="font-size: 1.5rem; color: ${parseFloat(sleepDebt) > 3 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
                ${parseFloat(sleepDebt).toFixed(1)} hrs
              </div>
            </div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 0.85rem; border-radius: 8px; border: 1px solid var(--border-subtle); font-size: 0.85rem;">
            <strong>Recovery State:</strong> ${recData.recovery_status || recData.recommendations || 'Adequate restorative sleep logged.'}
          </div>
        `;
      }
    } catch {}
  }

  async function loadExerciseStrength(exerciseId) {
    try {
      const data = await window.api.getStrengthAnalytics(exerciseId);
      const canvas = document.getElementById('strength-curve-canvas');
      if (canvas && data.history) {
        const labels = data.history.map(h => h.workout_date || h.session_date);
        const values = data.history.map(h => parseFloat(h.estimated_1rm_kg || h.estimated_1rm || 0));
        window.ProgressCharts.drawLineChart(canvas, {
          labels,
          values,
          unit: 'kg',
          title: data.exercise_name
        });
      }

      // Slope display
      const slopeVal = document.getElementById('slope-value');
      if (slopeVal) {
        const rawSlope = data.weekly_slope_kg ?? data.weekly_progression_slope;
        const slope = rawSlope !== null && rawSlope !== undefined ? parseFloat(rawSlope) : null;
        slopeVal.textContent = slope !== null ? `${slope > 0 ? '+' : ''}${slope.toFixed(2)} kg/week` : 'Insufficient history';
      }

      // Overload Diagnostics
      loadOverloadDiagnostic(exerciseId);
    } catch (err) {
      console.warn('Strength analytics error:', err);
    }
  }

  async function loadOverloadDiagnostic(exerciseId) {
    const container = document.getElementById('overload-diagnostic-container');
    try {
      const data = await window.api.getOverloadAnalytics(exerciseId);
      const isOverload = data.status === 'OVERLOAD_ACHIEVED';
      const badgeColor = isOverload ? 'var(--accent-emerald)' : data.status === 'PLATEAU' ? 'var(--accent-amber)' : 'var(--accent-rose)';
      const pathway = data.overload_dimension || data.pathway || 'STANDARD';
      const explanation = data.explanation || data.details || 'Overload comparison evaluated.';

      container.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
          <span style="font-weight: 700; font-size: 1rem;">${data.exercise_name}</span>
          <span style="background: rgba(255,255,255,0.06); border: 1px solid ${badgeColor}; color: ${badgeColor}; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 800; font-size: 0.75rem; letter-spacing: 0.05em;">
            ${data.status}
          </span>
        </div>
        <div style="background: rgba(255,255,255,0.02); padding: 0.85rem; border-radius: 8px; border: 1px solid var(--border-subtle); margin-bottom: 0.75rem;">
          <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Dimension: <strong>${pathway}</strong></div>
          <div style="font-size: 0.85rem; font-weight: 600; color: #f8fafc;">${explanation}</div>
        </div>
      `;
    } catch {
      container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">Need at least 2 sessions to evaluate progressive overload.</p>';
    }
  }

  document.getElementById('select-strength-exercise')?.addEventListener('change', (e) => {
    loadExerciseStrength(e.target.value);
  });

  // ==========================================================================
  // 5. Recommendations Report
  // ==========================================================================
  async function loadRecommendationsData() {
    if (!window.api.isAuthenticated()) return;
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '<p style="color: var(--text-muted);">Evaluating sports-science rules against your logs...</p>';

    try {
      const report = await window.api.getComprehensiveReport();

      // Energy balance cards
      if (report.energy_balance) {
        document.getElementById('rec-bmr-val').textContent = `${Math.round(report.energy_balance.bmr)} kcal`;
        document.getElementById('rec-tdee-val').textContent = `${Math.round(report.energy_balance.tdee)} kcal`;
        document.getElementById('rec-protein-val').textContent = `${Math.round(report.energy_balance.target_protein_g)} g/day`;
        document.getElementById('rec-water-val').textContent = `${report.energy_balance.water_benchmark_l?.toFixed(1) || 3.0} L/day`;
      } else {
        const p = await window.api.getProfile().catch(() => null);
        if (p && p.height_cm && (p.weight_kg || p.target_weight_kg)) {
          const w = parseFloat(p.weight_kg || p.target_weight_kg);
          const h = parseFloat(p.height_cm);
          const birthDate = new Date(p.birth_date || p.date_of_birth || '1998-01-01');
          const age = Math.max(18, Math.floor((new Date() - birthDate) / (365.25 * 24 * 3600 * 1000)));
          const bmr = p.gender === 'female' ? (10 * w + 6.25 * h - 5 * age - 161) : (10 * w + 6.25 * h - 5 * age + 5);
          const pals = { sedentary: 1.2, lightly_active: 1.375, moderately_active: 1.55, very_active: 1.725, extra_active: 1.9 };
          const tdee = bmr * (pals[p.activity_level] || 1.55);
          const targetProtein = Math.round(w * 2.0);
          const water = (w * 0.04).toFixed(1);
          document.getElementById('rec-bmr-val').textContent = `${Math.round(bmr)} kcal`;
          document.getElementById('rec-tdee-val').textContent = `${Math.round(tdee)} kcal`;
          document.getElementById('rec-protein-val').textContent = `${targetProtein} g/day`;
          document.getElementById('rec-water-val').textContent = `${water} L/day`;
        }
      }

      // Recommendations list
      const items = report.recommendations || [];
      if (items.length === 0) {
        container.innerHTML = `
          <div class="glass-card" style="text-align: center; padding: 2rem;">
            <p style="color: var(--accent-emerald); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">Optimal Progression Status</p>
            <p style="color: var(--text-muted); font-size: 0.88rem;">No training fatigue, overreaching, or nutrition deficits detected. Keep executing your program!</p>
          </div>`;
        return;
      }

      container.innerHTML = items.map(rec => {
        const sev = (rec.severity || rec.priority || 'INFO').toLowerCase();
        const cardClass = (sev === 'critical' || sev === 'action_required') ? 'critical' : sev === 'warning' ? 'warning' : 'info';
        const ruleId = rec.rule_id || rec.rule_code || 'RULE';
        const title = rec.title || rec.actionable_guidance || rec.actionable_recommendation || '';
        const rationale = rec.rationale || rec.trigger_reason || '';
        const guidance = rec.actionable_guidance || rec.actionable_recommendation || '';
        const category = rec.category || 'TRAINING';
        return `
          <div class="rec-card ${cardClass}">
            <div class="rec-meta">
              <span class="rec-tag ${cardClass}">${sev.toUpperCase()} PRIORITY</span>
              <span style="color: var(--text-muted); font-size: 0.75rem; font-family: var(--font-mono);">${ruleId} &bull; ${category}</span>
            </div>
            <div class="rec-message">${title}</div>
            <div class="rec-rationale"><strong>Trigger Reason:</strong> ${rationale}</div>
            <div class="rec-action">
              <span>💡 Prescription:</span>
              <span>${guidance}</span>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      container.innerHTML = `<p style="color: var(--accent-rose);">Failed to generate diagnostic report: ${err.message}</p>`;
    }
  }

  document.getElementById('refresh-recs-btn')?.addEventListener('click', loadRecommendationsData);

  // ==========================================================================
  // 6. Athlete Profile Form
  // ==========================================================================
  async function loadProfileData() {
    if (!window.api.isAuthenticated()) return;
    try {
      const p = await window.api.getProfile();
      if (p) {
        document.getElementById('profile-height').value = p.height_cm || '';
        document.getElementById('profile-weight').value = p.weight_kg || '';
        document.getElementById('profile-birthdate').value = p.birth_date || '';
        document.getElementById('profile-gender').value = p.gender || 'male';
        document.getElementById('profile-goal').value = p.primary_goal || 'hypertrophy';
        document.getElementById('profile-experience').value = p.experience_level || 'intermediate';
        document.getElementById('profile-activity').value = p.activity_level || 'moderately_active';
      }
    } catch {}
  }

  document.getElementById('form-athlete-profile')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      height_cm: parseFloat(document.getElementById('profile-height').value),
      weight_kg: parseFloat(document.getElementById('profile-weight').value),
      birth_date: document.getElementById('profile-birthdate').value,
      gender: document.getElementById('profile-gender').value,
      primary_goal: document.getElementById('profile-goal').value,
      experience_level: document.getElementById('profile-experience').value,
      activity_level: document.getElementById('profile-activity').value
    };

    try {
      await window.api.updateProfile(payload).catch(async () => {
        await window.api.createProfile(payload);
      });
      showToast('Athlete profile saved successfully', 'success');
      loadOverviewData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // ==========================================================================
  // Interactive Modal: Log Workout Session
  // ==========================================================================
  async function openWorkoutModal() {
    if (exercisesList.length === 0) {
      await loadExercisesCatalog();
    }
    setTodayDateInputs();
    const container = document.getElementById('modal-exercises-container');
    container.innerHTML = '';
    addExerciseCardToModal(); // Add first exercise card by default
    modalWorkout.classList.add('active');
  }

  function closeWorkoutModal() {
    modalWorkout.classList.remove('active');
  }

  document.getElementById('open-log-workout-btn')?.addEventListener('click', openWorkoutModal);
  document.getElementById('btn-log-workout-top')?.addEventListener('click', openWorkoutModal);
  document.getElementById('close-modal-workout-btn')?.addEventListener('click', closeWorkoutModal);
  document.getElementById('btn-cancel-workout')?.addEventListener('click', closeWorkoutModal);

  function addExerciseCardToModal() {
    const container = document.getElementById('modal-exercises-container');
    const cardId = `ex-${Date.now()}`;

    const card = document.createElement('div');
    card.className = 'workout-exercise-card';
    card.id = cardId;

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <select class="form-select select-exercise-id" style="max-width: 260px;" required>
          <option value="" disabled selected>-- Select Movement --</option>
          ${exercisesList.map(e => `<option value="${e.id}">${e.name} (${e.primary_muscle_group || e.target_muscle_group || 'General'})</option>`).join('')}
        </select>
        <button type="button" class="btn btn-danger btn-sm btn-remove-exercise">Remove</button>
      </div>

      <div class="sets-list-container">
        <!-- Sets rows will go here -->
      </div>

      <button type="button" class="btn btn-secondary btn-sm btn-add-set-row" style="margin-top: 0.5rem;">+ Add Set</button>
    `;

    // Event: Remove exercise card
    card.querySelector('.btn-remove-exercise').addEventListener('click', () => card.remove());

    // Event: Add Set row
    const setsList = card.querySelector('.sets-list-container');
    card.querySelector('.btn-add-set-row').addEventListener('click', () => addSetRow(setsList));

    // Pre-populate with 3 default sets
    addSetRow(setsList, 60, 10, 8);
    addSetRow(setsList, 60, 10, 8.5);
    addSetRow(setsList, 60, 8, 9);

    container.appendChild(card);
  }

  function addSetRow(container, defWeight = '', defReps = '', defRpe = '') {
    const setNum = container.children.length + 1;
    const row = document.createElement('div');
    row.className = 'set-row';
    row.innerHTML = `
      <span class="set-badge">#${setNum}</span>
      <input type="number" step="0.5" class="form-input input-set-weight" placeholder="kg" value="${defWeight}" required>
      <input type="number" class="form-input input-set-reps" placeholder="reps" value="${defReps}" required>
      <input type="number" step="0.5" class="form-input input-set-rpe" placeholder="RPE" value="${defRpe}" min="1" max="10">
      <button type="button" class="btn btn-secondary btn-icon" style="height: 32px; width: 32px;" title="Remove set">✕</button>
    `;
    row.querySelector('button').addEventListener('click', () => {
      row.remove();
      // Re-index remaining sets
      Array.from(container.children).forEach((r, idx) => {
        r.querySelector('.set-badge').textContent = `#${idx + 1}`;
      });
    });
    container.appendChild(row);
  }

  document.getElementById('btn-add-exercise-card')?.addEventListener('click', addExerciseCardToModal);

  // Submit Workout Session
  document.getElementById('form-log-workout')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const date = document.getElementById('workout-input-date').value;
    const duration = parseInt(document.getElementById('workout-input-duration').value);
    const notes = document.getElementById('workout-input-notes').value || null;

    const exerciseCards = document.querySelectorAll('.workout-exercise-card');
    if (exerciseCards.length === 0) {
      showToast('Please add at least one exercise', 'error');
      return;
    }

    const exercisesPayload = [];
    for (let i = 0; i < exerciseCards.length; i++) {
      const card = exerciseCards[i];
      const exerciseId = parseInt(card.querySelector('.select-exercise-id').value);
      if (!exerciseId) {
        showToast(`Please select an exercise for Movement #${i + 1}`, 'error');
        return;
      }

      const setRows = card.querySelectorAll('.set-row');
      if (setRows.length === 0) {
        showToast(`Please add at least one set for Movement #${i + 1}`, 'error');
        return;
      }

      const setsPayload = [];
      setRows.forEach((row, sIdx) => {
        setsPayload.push({
          set_number: sIdx + 1,
          weight_kg: parseFloat(row.querySelector('.input-set-weight').value),
          reps: parseInt(row.querySelector('.input-set-reps').value),
          rpe: row.querySelector('.input-set-rpe').value ? parseFloat(row.querySelector('.input-set-rpe').value) : null
        });
      });

      exercisesPayload.push({
        exercise_id: exerciseId,
        order: i + 1,
        exercise_sets: setsPayload
      });
    }

    try {
      await window.api.createWorkout({
        title: notes ? notes.slice(0, 100) : `Workout Session - ${date}`,
        workout_date: date,
        duration_minutes: duration,
        notes: notes,
        workout_exercises: exercisesPayload
      });
      showToast('Workout session logged successfully!', 'success');
      closeWorkoutModal();
      switchTab('workouts');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // ==========================================================================
  // Auth Modal & One-Click Demo
  // ==========================================================================
  function openAuthModal() {
    modalAuth.classList.add('active');
  }

  function closeAuthModal() {
    modalAuth.classList.remove('active');
  }

  authActionBtn?.addEventListener('click', () => {
    if (window.api.isAuthenticated()) {
      window.api.logout();
      updateAuthUI();
      showToast('Signed out', 'info');
      switchTab('overview');
    } else {
      openAuthModal();
    }
  });

  document.getElementById('close-modal-auth-btn')?.addEventListener('click', closeAuthModal);

  async function performDemoLogin() {
    try {
      await window.api.login('demo@progresspro.com', 'Password123!');
      updateAuthUI();
      closeAuthModal();
      showToast('Welcome back, Demo Athlete!', 'success');
      await loadExercisesCatalog();
      switchTab('overview');
    } catch (err) {
      showToast(`Demo login failed: ${err.message}. Please verify the database is seeded.`, 'error');
    }
  }

  quickDemoBtn?.addEventListener('click', performDemoLogin);
  btnDemoAuthFill?.addEventListener('click', performDemoLogin);

  document.getElementById('auth-toggle-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    isRegisterMode = !isRegisterMode;
    document.getElementById('modal-auth-title').textContent = isRegisterMode ? 'Athlete Registration' : 'Athlete Sign In';
    document.getElementById('btn-auth-submit').textContent = isRegisterMode ? 'Create Account' : 'Sign In';
    document.getElementById('group-auth-name').style.display = isRegisterMode ? 'block' : 'none';
    document.getElementById('auth-toggle-text').textContent = isRegisterMode ? 'Already have an account?' : "Don't have an account?";
    document.getElementById('auth-toggle-link').textContent = isRegisterMode ? ' Sign In' : ' Register';
  });

  document.getElementById('form-auth')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;
    const fullName = document.getElementById('auth-name').value || null;

    try {
      if (isRegisterMode) {
        await window.api.register(email, password, fullName);
        showToast('Registration successful! Signing in...', 'success');
      }
      await window.api.login(email, password);
      updateAuthUI();
      closeAuthModal();
      showToast('Authenticated successfully', 'success');
      await loadExercisesCatalog();
      switchTab('overview');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // ==========================================================================
  // Initialization Sequence
  // ==========================================================================
  checkApiHealth();
  updateAuthUI();
  loadExercisesCatalog();
  if (window.api.isAuthenticated()) {
    loadOverviewData();
  }
});
