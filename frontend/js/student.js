// Student State
let currentStudent = null;
let currentQuestion = null;
let selectedOption = null;
let startTime = null;
let timerInterval = null;
let stats = {
    answered: 0,
    correct: 0,
    streak: 0
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await initStudent();
    updateStats();
});

async function initStudent() {
    // Try to get existing student from localStorage or create new
    const savedStudent = localStorage.getItem('luminaStudent');
    if (savedStudent) {
        currentStudent = JSON.parse(savedStudent);
    } else {
        // Create default student
        try {
            const student = await api.createStudent(
                'Learner ' + Math.floor(Math.random() * 1000),
                'learner' + Date.now() + '@example.com'
            );
            currentStudent = student;
            localStorage.setItem('luminaStudent', JSON.stringify(student));
        } catch (e) {
            console.error('Failed to create student:', e);
        }
    }

    document.getElementById('student-name').textContent = currentStudent?.name || 'Student';
    document.getElementById('welcome-name').textContent = currentStudent?.name?.split(' ')[0] || 'Learner';

    // Load progress
    loadProgress();
}

function selectTopic(topic) {
    if (topic === 'Custom') {
        document.getElementById('custom-topic-section').classList.remove('hidden');
        return;
    }

    document.getElementById('custom-topic-section').classList.add('hidden');
    loadQuestion(topic);
}

async function generateCustomQuestion() {
    const topic = document.getElementById('custom-topic').value.trim();
    if (!topic) return;
    loadQuestion(topic);
}

async function loadQuestion(topic, difficulty = 'medium') {
    showLoading();

    try {
        // Use AI to generate question
        const question = await api.generateQuestion(topic, difficulty);
        currentQuestion = {
            ...question,
            topic: topic,
            correctAnswer: question.correct_answer,
            options: question.options
        };

        displayQuestion();
    } catch (error) {
        alert('Failed to generate question. Please try again.');
        console.error(error);
    }
}

function displayQuestion() {
    document.getElementById('welcome-section').classList.add('hidden');
    document.querySelector('.flex-wrap.justify-center').classList.add('hidden');
    document.getElementById('custom-topic-section')?.classList.add('hidden');
    document.getElementById('feedback-section').classList.add('hidden');

    const quizCard = document.getElementById('quiz-card');
    quizCard.classList.remove('hidden');

    document.getElementById('quiz-topic-badge').textContent = currentQuestion.topic;
    document.getElementById('question-text').textContent = currentQuestion.question;

    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';

    currentQuestion.options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'w-full p-4 text-left border-2 border-[#e6f4ef] rounded-xl hover:border-[#019863] hover:bg-[#f8fcfa] transition-all text-[#0c1c17] font-medium';
        btn.textContent = option;
        btn.onclick = () => selectOption(index, btn);
        optionsContainer.appendChild(btn);
    });

    // Reset state
    selectedOption = null;
    document.getElementById('submit-btn').disabled = true;
    document.getElementById('hint-display').classList.add('hidden');
    document.getElementById('hint-btn').classList.remove('hidden');

    // Start timer
    startTime = Date.now();
    startTimer();
}

function selectOption(index, btnElement) {
    // Clear previous selection
    document.querySelectorAll('#options-container button').forEach(btn => {
        btn.classList.remove('border-[#019863]', 'bg-[#e6f4ef]');
    });

    // Select new
    btnElement.classList.add('border-[#019863]', 'bg-[#e6f4ef]');
    selectedOption = index;
    document.getElementById('submit-btn').disabled = false;
}

async function getHint() {
    if (!currentQuestion) return;

    try {
        const hint = await api.getHint(
            currentQuestion.topic,
            currentQuestion.question,
            currentStudent.id
        );

        const hintDisplay = document.getElementById('hint-display');
        hintDisplay.textContent = '💡 ' + hint.hint;
        hintDisplay.classList.remove('hidden');
        document.getElementById('hint-btn').classList.add('hidden');
    } catch (error) {
        console.error('Failed to get hint:', error);
    }
}

async function submitAnswer() {
    if (selectedOption === null || !currentQuestion) return;

    clearInterval(timerInterval);
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);
    const studentAnswer = currentQuestion.options[selectedOption];

    try {
        const result = await api.submitAnswer({
            student_id: currentStudent.id,
            topic: currentQuestion.topic,
            question: currentQuestion.question,
            correct_answer: currentQuestion.correctAnswer,
            student_answer: studentAnswer,
            time_taken_seconds: timeTaken
        });

        showFeedback(result, studentAnswer);
        updateStats();

        // Check for mistakes to review
        if (!result.is_correct) {
            loadRecentMistakes();
        }
    } catch (error) {
        console.error('Submit failed:', error);
        alert('Failed to submit answer. Please try again.');
    }
}

function showFeedback(result, studentAnswer) {
    document.getElementById('quiz-card').classList.add('hidden');
    const feedbackSection = document.getElementById('feedback-section');
    feedbackSection.classList.remove('hidden');

    const feedbackCard = document.getElementById('feedback-card');
    const feedbackIcon = document.getElementById('feedback-icon');
    const feedbackTitle = document.getElementById('feedback-title');
    const aiFeedback = document.getElementById('ai-feedback');

    if (result.is_correct) {
        feedbackCard.className = 'rounded-2xl p-8 mb-6 border-2 bg-[#f0fdf4] border-[#019863]';
        feedbackIcon.textContent = '🎉';
        feedbackTitle.textContent = 'Correct!';
        feedbackTitle.className = 'text-2xl font-bold text-[#019863]';
        stats.streak++;
    } else {
        feedbackCard.className = 'rounded-2xl p-8 mb-6 border-2 bg-[#fef2f2] border-[#dc2626]';
        feedbackIcon.textContent = '💪';
        feedbackTitle.textContent = 'Keep Learning';
        feedbackTitle.className = 'text-2xl font-bold text-[#dc2626]';
        stats.streak = 0;
    }

    aiFeedback.textContent = result.feedback;
    stats.answered++;
    if (result.is_correct) stats.correct++;
}

function nextQuestion() {
    document.getElementById('feedback-section').classList.add('hidden');
    document.getElementById('welcome-section').classList.remove('hidden');
    document.querySelector('.flex-wrap.justify-center').classList.remove('hidden');
}

function showExplanation() {
    // Show detailed explanation from AI
    alert('Detailed explanation would open in a modal here!');
}

async function loadProgress() {
    try {
        const progress = await api.getStudentProgress(currentStudent.id);
        if (progress) {
            stats.correct = progress.topics.reduce((sum, t) => sum + t.correct_count, 0);
            stats.answered = progress.topics.reduce((sum, t) => sum + t.total_attempts, 0);
            updateStats();
        }
    } catch (e) {
        console.error('Failed to load progress:', e);
    }
}

async function loadRecentMistakes() {
    try {
        const mistakes = await api.getRecentMistakes(currentStudent.id, 3);
        if (mistakes.length > 0) {
            const section = document.getElementById('mistakes-section');
            section.classList.remove('hidden');

            const list = document.getElementById('mistakes-list');
            list.innerHTML = mistakes.map(m => `
                <div class="bg-[#f8fcfa] rounded-lg p-4 border-l-4 border-[#dc2626]">
                    <div class="font-bold text-[#0c1c17] mb-1">${m.topic}</div>
                    <div class="text-sm text-[#46a080] mb-2">${m.question}</div>
                    <div class="text-sm text-[#dc2626]">Your answer: ${m.student_answer}</div>
                    <div class="text-sm text-[#019863]">Correct: ${m.correct_answer}</div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Failed to load mistakes:', e);
    }
}

function updateStats() {
    const accuracy = stats.answered > 0 ? Math.round((stats.correct / stats.answered) * 100) : 0;
    document.getElementById('stat-accuracy').textContent = accuracy + '%';
    document.getElementById('accuracy-bar').style.width = accuracy + '%';
    document.getElementById('stat-answered').textContent = stats.answered;
    document.getElementById('stat-streak').textContent = stats.streak + ' 🔥';
}

function startTimer() {
    clearInterval(timerInterval);
    const timerEl = document.getElementById('timer');
    let seconds = 0;

    timerInterval = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        timerEl.textContent = `${mins}:${secs}`;
    }, 1000);
}

function showLoading() {
    document.getElementById('question-text').textContent = 'Generating your personalized question...';
}

function toggleTheme() {
    // Simple dark mode toggle
    document.body.classList.toggle('bg-[#10231c]');
    // In a full implementation, this would toggle dark mode classes throughout
    alert('Dark mode toggle would be implemented here!');
}