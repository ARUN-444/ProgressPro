/**
 * ProgressPro HTML5 Canvas Charting Engine
 * Zero-dependency, high-DPI retina-ready canvas visualizations
 * for strength curves, volume landmarks, and composite progress scores.
 */

class ProgressCharts {
  /**
   * Setup canvas for crisp high-DPI displays
   */
  static setupCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    
    // Set display size
    const width = rect.width || 300;
    const height = rect.height || 200;

    canvas.width = width * dpr;
    canvas.height = height * dpr;

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx, width, height };
  }

  /**
   * Draw Radial Progress Gauge (e.g. Overall Progress Score 0-100)
   */
  static drawRadialProgress(canvas, score, subtitle = 'PROGRESS SCORE') {
    const { ctx, width, height } = this.setupCanvas(canvas);
    ctx.clearRect(0, 0, width, height);

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 22;
    const strokeWidth = 14;

    // Background track
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = strokeWidth;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Progress arc
    const normalizedScore = Math.max(0, Math.min(100, score || 0));
    const startAngle = -Math.PI / 2;
    const endAngle = startAngle + (Math.PI * 2 * (normalizedScore / 100));

    // Gradient based on score tier
    const gradient = ctx.createLinearGradient(centerX - radius, centerY, centerX + radius, centerY);
    if (normalizedScore >= 75) {
      gradient.addColorStop(0, '#00f2fe');
      gradient.addColorStop(1, '#10b981');
    } else if (normalizedScore >= 50) {
      gradient.addColorStop(0, '#00f2fe');
      gradient.addColorStop(1, '#f59e0b');
    } else {
      gradient.addColorStop(0, '#f59e0b');
      gradient.addColorStop(1, '#f43f5e');
    }

    // Glow effect
    ctx.save();
    ctx.shadowColor = normalizedScore >= 75 ? 'rgba(16, 185, 129, 0.35)' : 'rgba(0, 242, 254, 0.35)';
    ctx.shadowBlur = 12;

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.strokeStyle = gradient;
    ctx.lineWidth = strokeWidth;
    ctx.lineCap = 'round';
    ctx.stroke();
    ctx.restore();

    // Central Value
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';
    ctx.font = '800 2.25rem "JetBrains Mono", monospace';
    ctx.fillText(`${Math.round(normalizedScore)}`, centerX, centerY - 6);

    // Subtitle
    ctx.fillStyle = '#94a3b8';
    ctx.font = '600 0.72rem "Plus Jakarta Sans", sans-serif';
    ctx.letterSpacing = '0.08em';
    ctx.fillText(subtitle, centerX, centerY + 22);
  }

  /**
   * Draw Line Chart (1RM progression, Weight trajectory)
   */
  static drawLineChart(canvas, { labels = [], values = [], unit = 'kg', title = '' }) {
    const { ctx, width, height } = this.setupCanvas(canvas);
    ctx.clearRect(0, 0, width, height);

    if (!values || values.length === 0) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#64748b';
      ctx.font = '600 0.9rem "Plus Jakarta Sans", sans-serif';
      ctx.fillText('No history data logged yet', width / 2, height / 2);
      return;
    }

    const padding = { top: 30, right: 25, bottom: 40, left: 45 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const minVal = Math.floor(Math.min(...values) * 0.95);
    const maxVal = Math.ceil(Math.max(...values) * 1.05);
    const range = maxVal - minVal || 1;

    // Horizontal grid lines
    const gridLines = 4;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#64748b';
    ctx.font = '500 0.72rem "JetBrains Mono", monospace';
    ctx.textAlign = 'right';

    for (let i = 0; i <= gridLines; i++) {
      const y = padding.top + (chartHeight / gridLines) * i;
      const val = Math.round(maxVal - (range / gridLines) * i);
      
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      ctx.fillText(`${val}${unit}`, padding.left - 8, y + 3);
    }

    // Coordinates calculation
    const points = values.map((val, idx) => {
      const x = padding.left + (chartWidth / (values.length - 1 || 1)) * idx;
      const y = padding.top + chartHeight - ((val - minVal) / range) * chartHeight;
      return { x, y, val, label: labels[idx] || '' };
    });

    // Fill under curve
    if (points.length > 1) {
      const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
      gradient.addColorStop(0, 'rgba(0, 242, 254, 0.22)');
      gradient.addColorStop(1, 'rgba(0, 242, 254, 0.0)');

      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }
      ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
      ctx.lineTo(points[0].x, height - padding.bottom);
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();
    }

    // Stroke line
    ctx.beginPath();
    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    points.forEach((pt, i) => {
      if (i === 0) ctx.moveTo(pt.x, pt.y);
      else ctx.lineTo(pt.x, pt.y);
    });
    ctx.stroke();

    // Data points & X labels
    ctx.textAlign = 'center';
    points.forEach((pt, i) => {
      // Outer glow
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 4.5, 0, Math.PI * 2);
      ctx.fillStyle = '#070b14';
      ctx.strokeStyle = '#00f2fe';
      ctx.lineWidth = 2;
      ctx.fill();
      ctx.stroke();

      // X Label (date or session #)
      ctx.fillStyle = '#94a3b8';
      ctx.font = '500 0.7rem "Plus Jakarta Sans", sans-serif';
      const displayLabel = pt.label.length > 5 ? pt.label.slice(5) : pt.label;
      ctx.fillText(displayLabel, pt.x, height - padding.bottom + 18);
    });
  }

  /**
   * Draw Dr. Mike Israetel Volume Landmarks Bar Chart
   * (Sets per muscle group vs MEV:10, MAV:14, MRV:20)
   */
  static drawVolumeLandmarksChart(canvas, muscleData = {}) {
    const { ctx, width, height } = this.setupCanvas(canvas);
    ctx.clearRect(0, 0, width, height);

    const muscles = Object.keys(muscleData);
    if (muscles.length === 0) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#64748b';
      ctx.font = '600 0.9rem "Plus Jakarta Sans", sans-serif';
      ctx.fillText('No workout volume recorded this week', width / 2, height / 2);
      return;
    }

    const padding = { top: 25, right: 30, bottom: 45, left: 45 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const maxSets = 25; // Standard ceiling for landmark comparisons

    // Landmark threshold reference lines
    const landmarks = [
      { name: 'MEV', sets: 10, color: 'rgba(245, 158, 11, 0.4)' },
      { name: 'MAV', sets: 14, color: 'rgba(0, 242, 254, 0.4)' },
      { name: 'MRV', sets: 20, color: 'rgba(244, 63, 94, 0.4)' }
    ];

    landmarks.forEach(lm => {
      const y = padding.top + chartHeight - (lm.sets / maxSets) * chartHeight;
      ctx.strokeStyle = lm.color;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = lm.color;
      ctx.font = '600 0.68rem "JetBrains Mono", monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`${lm.name} (${lm.sets})`, width - padding.right + 4, y + 3);
    });

    // Draw Bars
    const barWidth = Math.min(42, (chartWidth / muscles.length) * 0.65);
    const gap = chartWidth / muscles.length;

    muscles.forEach((muscle, i) => {
      const sets = muscleData[muscle] || 0;
      const barHeight = (Math.min(sets, maxSets) / maxSets) * chartHeight;
      const x = padding.left + gap * i + (gap - barWidth) / 2;
      const y = padding.top + chartHeight - barHeight;

      // Color tier by landmark
      let barColor = '#00f2fe';
      if (sets < 10) barColor = '#f59e0b'; // Below MEV
      else if (sets >= 10 && sets < 14) barColor = '#00f2fe'; // MEV-MAV
      else if (sets >= 14 && sets <= 20) barColor = '#10b981'; // MAV-MRV Optimal
      else if (sets > 20) barColor = '#f43f5e'; // Above MRV (Overreaching)

      // Bar rounded top
      ctx.fillStyle = barColor;
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, [4, 4, 0, 0]);
      ctx.fill();

      // Sets count on top of bar
      ctx.fillStyle = '#ffffff';
      ctx.font = '700 0.75rem "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`${sets}`, x + barWidth / 2, y - 6);

      // Muscle label below
      ctx.fillStyle = '#94a3b8';
      ctx.font = '600 0.72rem "Plus Jakarta Sans", sans-serif';
      ctx.fillText(muscle, x + barWidth / 2, height - padding.bottom + 18);
    });
  }
}

window.ProgressCharts = ProgressCharts;
