/**
 * Week 3 Respiratory MCQs - Web Application
 * Australian Medical Context
 *
 * Features:
 * - 200 MCQs with full Australian medical context
 * - Progress tracking with LocalStorage
 * - Topic filtering and view modes
 * - Answer checking with explanations
 * - Copy protection and security
 */

(function() {
    'use strict';

    // ============================================
    // APPLICATION STATE
    // ============================================
    const App = {
        mcqs: [],
        filteredMCQs: [],
        currentIndex: 0,
        currentMCQ: null,
        progress: {
            answered: new Set(),
            correct: new Set(),
            incorrect: new Set(),
            flagged: new Set()
        },
        filters: {
            topic: 'all',
            viewMode: 'all'
        },
        selectedAnswer: null,
        answerSubmitted: false
    };

    // ============================================
    // SECURITY & COPY PROTECTION
    // ============================================
    function initSecurity() {
        // Disable right-click
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });

        // Disable common keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl+C, Cmd+C (copy)
            if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'C')) {
                e.preventDefault();
                return false;
            }
            // Ctrl+U, Cmd+U (view source)
            if ((e.ctrlKey || e.metaKey) && (e.key === 'u' || e.key === 'U')) {
                e.preventDefault();
                return false;
            }
            // Ctrl+S, Cmd+S (save)
            if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
                e.preventDefault();
                return false;
            }
            // F12 (dev tools)
            if (e.key === 'F12') {
                e.preventDefault();
                return false;
            }
            // Ctrl+Shift+I, Cmd+Option+I (inspect)
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'i' || e.key === 'I')) {
                e.preventDefault();
                return false;
            }
            // Ctrl+Shift+J, Cmd+Option+J (console)
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'j' || e.key === 'J')) {
                e.preventDefault();
                return false;
            }
            // Ctrl+Shift+C, Cmd+Option+C (inspect element)
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'c' || e.key === 'C')) {
                e.preventDefault();
                return false;
            }
        });

        // Disable drag & drop
        document.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });

        // Disable text selection via mouse events
        document.addEventListener('selectstart', function(e) {
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                return false;
            }
        });

        // Simple DevTools detection
        const devtoolsCheck = setInterval(function() {
            const threshold = 160;
            const widthThreshold = window.outerWidth - window.innerWidth > threshold;
            const heightThreshold = window.outerHeight - window.innerHeight > threshold;

            if (widthThreshold || heightThreshold) {
                console.clear();
                console.log('%c⚠️ Developer Tools Detected', 'color: red; font-size: 20px; font-weight: bold;');
                console.log('%cThis application is protected. Please close developer tools.', 'color: orange; font-size: 14px;');
            }
        }, 1000);

        console.log('%c🔒 Content Protection Active', 'color: green; font-size: 16px; font-weight: bold;');
        console.log('%cThis application includes copy protection and content security measures.', 'color: blue; font-size: 12px;');
    }

    // ============================================
    // DATA LOADING
    // ============================================
    async function loadMCQs() {
        try {
            const response = await fetch('../data/mcqs.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // Extract MCQs array from the JSON structure
            if (data.mcqs && Array.isArray(data.mcqs)) {
                App.mcqs = data.mcqs;
            } else {
                throw new Error('Invalid MCQ data format');
            }

            console.log(`✅ Loaded ${App.mcqs.length} MCQs`);
            return App.mcqs;
        } catch (error) {
            console.error('Error loading MCQs:', error);
            alert('Failed to load MCQs. Please refresh the page.');
            throw error;
        }
    }

    // ============================================
    // LOCAL STORAGE (PROGRESS PERSISTENCE)
    // ============================================
    function loadProgress() {
        try {
            const saved = localStorage.getItem('respiratory-mcq-progress');
            if (saved) {
                const data = JSON.parse(saved);
                App.progress.answered = new Set(data.answered || []);
                App.progress.correct = new Set(data.correct || []);
                App.progress.incorrect = new Set(data.incorrect || []);
                App.progress.flagged = new Set(data.flagged || []);
                console.log(`📊 Loaded progress: ${App.progress.answered.size} answered`);
            }
        } catch (error) {
            console.error('Error loading progress:', error);
        }
    }

    function saveProgress() {
        try {
            const data = {
                answered: Array.from(App.progress.answered),
                correct: Array.from(App.progress.correct),
                incorrect: Array.from(App.progress.incorrect),
                flagged: Array.from(App.progress.flagged),
                lastUpdated: new Date().toISOString()
            };
            localStorage.setItem('respiratory-mcq-progress', JSON.stringify(data));
        } catch (error) {
            console.error('Error saving progress:', error);
        }
    }

    function resetProgress() {
        if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
            App.progress.answered.clear();
            App.progress.correct.clear();
            App.progress.incorrect.clear();
            App.progress.flagged.clear();
            localStorage.removeItem('respiratory-mcq-progress');
            updateStats();
            renderMCQ();
            alert('Progress has been reset.');
        }
    }

    // ============================================
    // FILTERING & VIEW MODES
    // ============================================
    function applyFilters() {
        let filtered = [...App.mcqs];

        // Topic filter
        if (App.filters.topic !== 'all') {
            filtered = filtered.filter(mcq => {
                const topic = mcq.topic || mcq.question?.topic || '';
                return topic.toLowerCase().includes(App.filters.topic.toLowerCase());
            });
        }

        // View mode filter
        if (App.filters.viewMode !== 'all') {
            filtered = filtered.filter((mcq, index) => {
                const mcqId = mcq.id;
                switch (App.filters.viewMode) {
                    case 'unanswered':
                        return !App.progress.answered.has(mcqId);
                    case 'incorrect':
                        return App.progress.incorrect.has(mcqId);
                    case 'flagged':
                        return App.progress.flagged.has(mcqId);
                    default:
                        return true;
                }
            });
        }

        App.filteredMCQs = filtered;
        App.currentIndex = 0;
        return filtered;
    }

    // ============================================
    // MCQ RENDERING
    // ============================================
    function renderMCQ() {
        const mcq = App.filteredMCQs[App.currentIndex];
        if (!mcq) {
            document.getElementById('mcq-container').innerHTML = '<p style="text-align: center; padding: 40px; font-size: 1.2rem;">No MCQs match the current filters.</p>';
            return;
        }

        App.currentMCQ = mcq;
        App.selectedAnswer = null;
        App.answerSubmitted = false;

        // Question number
        const questionNum = App.mcqs.indexOf(mcq) + 1;
        document.getElementById('question-number').textContent = `Q${questionNum}`;
        document.getElementById('current-question').textContent = `Question ${questionNum}`;

        // Scenario and stem
        const scenario = mcq.question?.scenario || '';
        const stem = mcq.question?.stem || mcq.question;

        document.getElementById('question-scenario').innerHTML = scenario;
        document.getElementById('question-stem').innerHTML = typeof stem === 'string' ? stem : '';

        // Options
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        const options = mcq.question?.options || mcq.options || {};
        Object.keys(options).sort().forEach(letter => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'option-item';
            optionDiv.dataset.letter = letter;

            // Check if already answered
            const isAnswered = App.progress.answered.has(mcq.id);
            const isCorrect = mcq.correct_answer === letter;

            if (isAnswered) {
                optionDiv.classList.add('disabled');
                if (isCorrect) {
                    optionDiv.classList.add('correct');
                } else if (App.progress.incorrect.has(mcq.id)) {
                    const userAnswer = getUserAnswer(mcq.id);
                    if (userAnswer === letter) {
                        optionDiv.classList.add('incorrect');
                    }
                }
            }

            optionDiv.innerHTML = `
                <div class="option-label">
                    <span class="option-letter">${letter}</span>
                    <span class="option-text">${options[letter]}</span>
                </div>
            `;

            if (!isAnswered) {
                optionDiv.addEventListener('click', () => selectOption(letter));
            }

            optionsContainer.appendChild(optionDiv);
        });

        // Update flag button
        const flagBtn = document.getElementById('flag-btn');
        if (App.progress.flagged.has(mcq.id)) {
            flagBtn.classList.add('flagged');
        } else {
            flagBtn.classList.remove('flagged');
        }

        // Hide/show buttons based on state
        const isAnswered = App.progress.answered.has(mcq.id);
        document.getElementById('submit-answer').style.display = isAnswered ? 'none' : 'inline-flex';
        document.getElementById('show-explanation').style.display = isAnswered ? 'inline-flex' : 'none';
        document.getElementById('submit-answer').disabled = true;

        // Hide feedback and explanation
        document.getElementById('feedback-section').style.display = 'none';
        document.getElementById('explanation-section').style.display = 'none';

        // Show explanation if already answered
        if (isAnswered) {
            showFeedback();
        }

        // Update navigation buttons
        updateNavigationButtons();
        updateStats();
        updateProgressBar();
    }

    function selectOption(letter) {
        if (App.answerSubmitted) return;

        // Remove previous selection
        document.querySelectorAll('.option-item').forEach(opt => {
            opt.classList.remove('selected');
        });

        // Add selection to clicked option
        const optionDiv = document.querySelector(`[data-letter="${letter}"]`);
        optionDiv.classList.add('selected');

        App.selectedAnswer = letter;
        document.getElementById('submit-answer').disabled = false;
    }

    // ============================================
    // ANSWER CHECKING
    // ============================================
    function submitAnswer() {
        if (!App.selectedAnswer || App.answerSubmitted) return;

        const mcq = App.currentMCQ;
        const correctAnswer = mcq.correct_answer;
        const isCorrect = App.selectedAnswer === correctAnswer;

        // Update progress
        App.progress.answered.add(mcq.id);
        if (isCorrect) {
            App.progress.correct.add(mcq.id);
            App.progress.incorrect.delete(mcq.id);
        } else {
            App.progress.incorrect.add(mcq.id);
            App.progress.correct.delete(mcq.id);
            // Store user's answer
            storeUserAnswer(mcq.id, App.selectedAnswer);
        }

        App.answerSubmitted = true;
        saveProgress();

        // Update UI
        showFeedback();
        updateStats();
        updateProgressBar();

        // Disable submit button, show explanation button
        document.getElementById('submit-answer').style.display = 'none';
        document.getElementById('show-explanation').style.display = 'inline-flex';

        // Disable all options
        document.querySelectorAll('.option-item').forEach(opt => {
            opt.classList.add('disabled');
            opt.style.pointerEvents = 'none';
        });

        // Highlight correct/incorrect
        const selectedOption = document.querySelector(`[data-letter="${App.selectedAnswer}"]`);
        const correctOption = document.querySelector(`[data-letter="${correctAnswer}"]`);

        if (isCorrect) {
            selectedOption.classList.add('correct');
        } else {
            selectedOption.classList.add('incorrect');
            correctOption.classList.add('correct');
        }
    }

    function showFeedback() {
        const mcq = App.currentMCQ;
        const isCorrect = App.progress.correct.has(mcq.id);

        const feedbackSection = document.getElementById('feedback-section');
        const feedbackMessage = document.getElementById('feedback-message');

        feedbackSection.style.display = 'block';
        feedbackSection.className = 'feedback-section ' + (isCorrect ? 'correct' : 'incorrect');
        feedbackMessage.textContent = isCorrect
            ? '✓ Correct! Well done.'
            : '✗ Incorrect. The correct answer is highlighted.';
    }

    function showExplanation() {
        const mcq = App.currentMCQ;
        const explanationSection = document.getElementById('explanation-section');

        // Explanation content
        document.getElementById('explanation-content').innerHTML = mcq.explanation || 'No explanation available.';
        document.getElementById('explanation-summary').textContent = mcq.summary || '';

        // Citations
        const citationsList = document.getElementById('citations-list');
        citationsList.innerHTML = '';

        const citations = mcq.citations || [];
        citations.forEach(citation => {
            const li = document.createElement('li');
            if (typeof citation === 'string') {
                li.textContent = citation;
            } else {
                li.textContent = citation.source || citation.citation || 'Unknown source';
            }
            citationsList.appendChild(li);
        });

        // Learning objectives
        const objectivesList = document.getElementById('learning-objectives-list');
        objectivesList.innerHTML = '';

        const objectives = mcq.learning_objectives || [];
        objectives.forEach(obj => {
            const li = document.createElement('li');
            li.textContent = obj;
            objectivesList.appendChild(li);
        });

        explanationSection.style.display = 'block';
        explanationSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // ============================================
    // NAVIGATION
    // ============================================
    function nextMCQ() {
        if (App.currentIndex < App.filteredMCQs.length - 1) {
            App.currentIndex++;
            renderMCQ();
            scrollToTop();
        }
    }

    function prevMCQ() {
        if (App.currentIndex > 0) {
            App.currentIndex--;
            renderMCQ();
            scrollToTop();
        }
    }

    function jumpToMCQ(number) {
        const index = number - 1;
        if (index >= 0 && index < App.mcqs.length) {
            // Find the MCQ in filtered list
            const targetMCQ = App.mcqs[index];
            const filteredIndex = App.filteredMCQs.indexOf(targetMCQ);

            if (filteredIndex !== -1) {
                App.currentIndex = filteredIndex;
                renderMCQ();
                scrollToTop();
            } else {
                alert('This MCQ is hidden by current filters.');
            }
        }
    }

    function updateNavigationButtons() {
        document.getElementById('prev-btn').disabled = App.currentIndex === 0;
        document.getElementById('next-btn').disabled = App.currentIndex === App.filteredMCQs.length - 1;
    }

    function scrollToTop() {
        document.querySelector('.mcq-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // ============================================
    // STATISTICS & PROGRESS
    // ============================================
    function updateStats() {
        document.getElementById('total-questions').textContent = App.mcqs.length;
        document.getElementById('answered-count').textContent = App.progress.answered.size;
        document.getElementById('correct-count').textContent = App.progress.correct.size;
        document.getElementById('flagged-count').textContent = App.progress.flagged.size;

        const scorePercent = App.progress.answered.size > 0
            ? Math.round((App.progress.correct.size / App.progress.answered.size) * 100)
            : 0;
        document.getElementById('score-display').textContent = `Score: ${scorePercent}%`;
    }

    function updateProgressBar() {
        const percent = (App.progress.answered.size / App.mcqs.length) * 100;
        document.getElementById('progress-fill').style.width = `${percent}%`;
    }

    // ============================================
    // FLAGGING
    // ============================================
    function toggleFlag() {
        const mcq = App.currentMCQ;
        if (App.progress.flagged.has(mcq.id)) {
            App.progress.flagged.delete(mcq.id);
        } else {
            App.progress.flagged.add(mcq.id);
        }
        saveProgress();
        updateStats();

        const flagBtn = document.getElementById('flag-btn');
        if (App.progress.flagged.has(mcq.id)) {
            flagBtn.classList.add('flagged');
        } else {
            flagBtn.classList.remove('flagged');
        }
    }

    // ============================================
    // HELPER FUNCTIONS
    // ============================================
    function storeUserAnswer(mcqId, answer) {
        try {
            const userAnswers = JSON.parse(localStorage.getItem('respiratory-mcq-user-answers') || '{}');
            userAnswers[mcqId] = answer;
            localStorage.setItem('respiratory-mcq-user-answers', JSON.stringify(userAnswers));
        } catch (error) {
            console.error('Error storing user answer:', error);
        }
    }

    function getUserAnswer(mcqId) {
        try {
            const userAnswers = JSON.parse(localStorage.getItem('respiratory-mcq-user-answers') || '{}');
            return userAnswers[mcqId];
        } catch (error) {
            return null;
        }
    }

    // ============================================
    // EVENT LISTENERS
    // ============================================
    function initEventListeners() {
        // Submit answer
        document.getElementById('submit-answer').addEventListener('click', submitAnswer);

        // Show explanation
        document.getElementById('show-explanation').addEventListener('click', showExplanation);

        // Navigation
        document.getElementById('prev-btn').addEventListener('click', prevMCQ);
        document.getElementById('next-btn').addEventListener('click', nextMCQ);

        // Jump to MCQ
        document.getElementById('jump-btn').addEventListener('click', () => {
            const num = parseInt(document.getElementById('jump-input').value);
            jumpToMCQ(num);
        });

        document.getElementById('jump-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const num = parseInt(e.target.value);
                jumpToMCQ(num);
            }
        });

        // Flag button
        document.getElementById('flag-btn').addEventListener('click', toggleFlag);

        // Filters
        document.getElementById('topic-filter').addEventListener('change', (e) => {
            App.filters.topic = e.target.value;
            applyFilters();
            renderMCQ();
        });

        document.getElementById('view-mode').addEventListener('change', (e) => {
            App.filters.viewMode = e.target.value;
            applyFilters();
            renderMCQ();
        });

        // Reset progress
        document.getElementById('reset-progress').addEventListener('click', resetProgress);

        // Keyboard shortcuts (Arrow keys for navigation)
        document.addEventListener('keydown', (e) => {
            // Don't trigger if user is typing in input
            if (e.target.tagName === 'INPUT') return;

            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                nextMCQ();
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                prevMCQ();
            } else if (e.key === ' ' && App.selectedAnswer && !App.answerSubmitted) {
                e.preventDefault();
                submitAnswer();
            }
        });
    }

    // ============================================
    // INITIALIZATION
    // ============================================
    async function init() {
        console.log('🚀 Initializing Respiratory MCQ App...');

        // Initialize security features
        initSecurity();

        // Load MCQs
        await loadMCQs();

        // Load saved progress
        loadProgress();

        // Apply initial filters
        applyFilters();

        // Initialize event listeners
        initEventListeners();

        // Render first MCQ
        renderMCQ();

        // Hide loading overlay
        document.getElementById('loading-overlay').classList.add('hidden');

        console.log('✅ App initialized successfully');
    }

    // Start the app when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
