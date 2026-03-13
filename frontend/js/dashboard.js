// Global state
let topicChart = null;
let isLoading = false;
let hasInitialized = false;

// Initialize once
document.addEventListener('DOMContentLoaded', () => {
    if (hasInitialized) {
        console.log('Already initialized, skipping...');
        return;
    }
    hasInitialized = true;

    console.log('Dashboard initializing...');
    setTimeout(loadDashboardData, 100);
});

async function loadDashboardData() {
    if (isLoading) {
        console.log('Load already in progress, skipping...');
        return;
    }

    isLoading = true;
    console.log('Loading dashboard data...');

    try {
        // Load in sequence to prevent race conditions
        await loadClassOverview();
        await new Promise(r => setTimeout(r, 50)); // Small delay between calls
        await loadStrugglingStudents();
        await new Promise(r => setTimeout(r, 50));
        await loadHardestTopic();
        await new Promise(r => setTimeout(r, 50));
        await loadTopicChart();
    } catch (error) {
        console.error('Dashboard load error:', error);
        showError('Failed to load dashboard. Is backend running?');
    } finally {
        isLoading = false;
    }
}

function showError(message) {
    const existing = document.getElementById('error-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'error-banner';
    banner.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
    banner.innerHTML = `<strong>Error:</strong> ${message} <button onclick="this.parentElement.remove()" class="ml-2 font-bold">×</button>`;

    const container = document.querySelector('.max-w-\\[1200px\\]');
    if (container) {
        container.insertBefore(banner, container.firstChild);
    }
}

async function refreshData() {
    const icon = document.getElementById('refresh-icon');
    if (icon) icon.classList.add('animate-spin');

    await loadDashboardData();

    if (icon) icon.classList.remove('animate-spin');
}

// ==================== TOPIC PERFORMANCE CHART ====================

async function loadTopicChart() {
    const canvas = document.getElementById('topicChart');
    if (!canvas) {
        console.error('Chart canvas not found!');
        return;
    }

    // CRITICAL: Destroy existing chart to prevent duplicates
    if (topicChart) {
        console.log('Destroying existing chart...');
        topicChart.destroy();
        topicChart = null;
    }

    // Reset canvas
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    try {
        const data = await api.getClassOverview();
        const topics = data?.topic_breakdown || [];

        console.log('Chart data received:', topics);

        if (topics.length === 0) {
            // Show "no data" message
            ctx.font = '14px Inter, sans-serif';
            ctx.fillStyle = '#46a080';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('No quiz data available yet', canvas.width / 2, canvas.height / 2);
            return;
        }

        // Create new chart
        topicChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topics.map(t => t.topic),
                datasets: [{
                    label: 'Accuracy %',
                    data: topics.map(t => t.accuracy || 0),
                    backgroundColor: topics.map(t => {
                        const acc = t.accuracy || 0;
                        return acc < 50 ? '#dc2626' : acc < 70 ? '#f59e0b' : '#019863';
                    }),
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: '#e6f4ef' },
                        ticks: { callback: (v) => v + '%' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });

        console.log('Chart created successfully');

    } catch (error) {
        console.error('Chart error:', error);
        ctx.font = '14px Inter, sans-serif';
        ctx.fillStyle = '#dc2626';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Error loading chart', canvas.width / 2, canvas.height / 2);
    }
}

// ==================== HARDEST TOPIC ====================

async function loadHardestTopic() {
    const nameEl = document.getElementById('hardest-topic-name');
    const accEl = document.getElementById('hardest-topic-accuracy');

    if (!nameEl || !accEl) {
        console.error('Hardest topic elements not found!');
        return;
    }

    // Set loading state once
    nameEl.textContent = 'Loading...';
    accEl.textContent = '-%';

    try {
        const data = await api.getHardestTopic();
        console.log('Hardest topic:', data);

        nameEl.textContent = data?.topic || 'No data available';
        accEl.textContent = (data?.avg_accuracy ?? 0) + '%';

    } catch (error) {
        console.error('Hardest topic error:', error);
        nameEl.textContent = 'Error loading data';
        accEl.textContent = '-%';
    }
}

// ==================== OTHER FUNCTIONS ====================

async function loadClassOverview() {
    const elStudents = document.getElementById('metric-total-students');
    const elAccuracy = document.getElementById('metric-class-accuracy');
    const elAttempts = document.getElementById('metric-total-attempts');

    if (!elStudents || !elAccuracy || !elAttempts) return;

    try {
        const data = await api.getClassOverview();
        elStudents.textContent = data?.total_students ?? 0;
        elAccuracy.textContent = (data?.overall_accuracy ?? 0) + '%';
        elAttempts.textContent = data?.total_attempts ?? 0;
    } catch (error) {
        console.error('Overview error:', error);
    }
}

async function loadStrugglingStudents() {
    const thresholdSelect = document.getElementById('threshold-select');
    const threshold = thresholdSelect?.value || 0.6;

    const elStruggling = document.getElementById('metric-struggling');
    const tbody = document.getElementById('struggling-students-table');

    if (!elStruggling || !tbody) return;

    try {
        const students = await api.getStrugglingStudents(threshold);
        elStruggling.textContent = Array.isArray(students) ? students.length : 0;

        if (!Array.isArray(students) || students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-[#46a080]">No students struggling at this threshold! 🎉</td></tr>';
            return;
        }

        tbody.innerHTML = students.map(s => {
            const accuracy = s?.overall_accuracy ?? 0;
            const isLow = accuracy < 50;

            return `<tr class="hover:bg-[#f8fcfa] transition-colors">
                <td class="px-6 py-4">
                    <div class="flex items-center">
                        <div class="h-8 w-8 rounded-full bg-[#e6f4ef] flex items-center justify-center text-[#019863] font-bold text-sm mr-3">
                            ${(s?.student_name || 'S').charAt(0)}
                        </div>
                        <div>
                            <div class="text-sm font-medium text-[#0c1c17]">${s?.student_name || 'Unknown'}</div>
                            <div class="text-xs text-[#46a080]">${s?.email || 'no email'}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4">
                    <div class="flex items-center">
                        <div class="w-16 bg-[#e6f4ef] rounded-full h-2 mr-2">
                            <div class="${isLow ? 'bg-red-500' : 'bg-yellow-500'} h-2 rounded-full" 
                                 style="width: ${Math.min(accuracy, 100)}%"></div>
                        </div>
                        <span class="text-sm font-medium ${isLow ? 'text-red-600' : 'text-yellow-600'}">
                            ${accuracy.toFixed(1)}%
                        </span>
                    </div>
                </td>
                <td class="px-6 py-4">
                    <div class="flex flex-wrap gap-1">
                        ${Array.isArray(s?.topics_struggling) && s.topics_struggling.length > 0
                    ? s.topics_struggling.map(t => `<span class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-medium">${t}</span>`).join('')
                    : '<span class="text-gray-400 text-sm">None</span>'
                }
                    </div>
                </td>
                <td class="px-6 py-4">
                    <button onclick="viewStudentDetails(${s?.student_id || 0})" class="text-[#019863] hover:text-[#017a4f] text-sm font-medium">
                        View →
                    </button>
                </td>
            </tr>`;
        }).join('');

    } catch (error) {
        console.error('Struggling students error:', error);
        tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-8 text-center text-red-500">
            Error loading data<br>
            <button onclick="loadStrugglingStudents()" class="mt-2 text-[#019863] underline">Retry</button>
        </td></tr>`;
    }
}

async function generateAIInsights() {
    const modal = document.getElementById('ai-insights-modal');
    const content = document.getElementById('ai-insights-content');

    if (!modal || !content) return;

    modal.classList.remove('hidden');
    content.innerHTML = `
        <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#019863]"></div>
            <span class="ml-2 text-[#46a080]">Analyzing...</span>
        </div>
    `;

    try {
        const students = await api.getStrugglingStudents(0.6);

        if (!Array.isArray(students) || students.length === 0) {
            content.innerHTML = '<p class="text-[#46a080] text-center py-4">No struggling students! 🎉</p>';
            return;
        }

        const student = students[0];
        const insights = await api.getAITeachingInsights(student.student_id);

        content.innerHTML = `
            <div class="mb-4">
                <h4 class="font-bold text-[#0c1c17] mb-2 text-lg">${student.student_name || 'Student'}</h4>
                <div class="bg-[#f8fcfa] p-4 rounded-lg border border-[#e6f4ef] max-h-96 overflow-y-auto">
                    <div class="whitespace-pre-wrap text-sm text-[#0c1c17] font-sans leading-relaxed">
                        ${insights?.ai_recommendations || 'No recommendations available'}
                    </div>
                </div>
            </div>
            <div class="text-sm text-[#46a080] bg-[#e6f4ef] p-3 rounded-lg">
                <strong>Weak Areas:</strong> ${Array.isArray(insights?.weak_areas) ? insights.weak_areas.map(w => w.topic).join(', ') : 'None'}
            </div>
        `;
    } catch (error) {
        content.innerHTML = `
            <div class="text-red-600 text-center py-4">
                <p class="font-bold mb-2">Failed to generate insights</p>
                <p class="text-sm">${error.message}</p>
                <button onclick="generateAIInsights()" class="mt-3 px-4 py-2 bg-[#019863] text-white rounded-lg text-sm">Retry</button>
            </div>
        `;
    }
}

function closeModal() {
    const modal = document.getElementById('ai-insights-modal');
    if (modal) modal.classList.add('hidden');
}

function viewStudentDetails(studentId) {
    alert(`Student ${studentId} details would open here.`);
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('ai-insights-modal');
    if (modal && e.target === modal) {
        closeModal();
    }
});