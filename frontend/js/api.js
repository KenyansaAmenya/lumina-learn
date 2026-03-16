/* local production 
const API_BASE_URL = 'http://localhost:8000'; */

/*Vercel*/
const API_BASE_URL = 'https://lumina-learn-five.vercel.app/'

class LuminaLearnAPI {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            console.log(`API Call: ${options.method || 'GET'} ${url}`);
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorText = await response.text();
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch {
                    errorData = { detail: errorText };
                }
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`API Response:`, data);
            return data;

        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Students
    async createStudent(name, email) {
        return this.request('/students', {
            method: 'POST',
            body: { name, email }
        });
    }

    async getStudent(studentId) {
        return this.request(`/students/${studentId}`);
    }

    // Quiz
    async submitAnswer(submission) {
        return this.request('/submit-answer', {
            method: 'POST',
            body: submission
        });
    }

    async generateQuestion(topic, difficulty = 'medium') {
        return this.request('/generate-question', {
            method: 'POST',
            body: { topic, difficulty }
        });
    }

    async getHint(topic, question, studentId) {
        return this.request('/get-hint', {
            method: 'POST',
            body: { topic, question, student_id: studentId }
        });
    }

    // Progress & Analytics
    async getStudentProgress(studentId) {
        return this.request(`/student-progress/${studentId}`);
    }

    async getRecentMistakes(studentId, limit = 5) {
        return this.request(`/recent-mistakes/${studentId}?limit=${limit}`);
    }

    async getStrugglingStudents(threshold = 0.6) {
        return this.request(`/analytics/struggling?threshold=${threshold}`);
    }

    async getHardestTopic() {
        return this.request('/analytics/hardest-topic');
    }

    async getClassOverview() {
        return this.request('/analytics/class-overview');
    }

    async getAITeachingInsights(studentId) {
        return this.request(`/analytics/ai-teaching-insights/${studentId}`, {
            method: 'POST'
        });
    }
}

const api = new LuminaLearnAPI();