// static/js/exercise_list.js - без автоматической инициализации
(function() {
    // Проверяем, инициализирован ли уже модуль
    if (window._exerciseListModule) {
        console.log('Exercise list module already initialized');
        return;
    }
    window._exerciseListModule = true;

    console.log('Exercise list module loaded');

    let state = {
        currentPage: 1,
        isLoading: false,
        hasMore: true,
        totalLoaded: 0
    };

    function getFilterParams() {
        const params = new URLSearchParams();
        const q = document.getElementById('search-input')?.value;
        const exercise_type = document.getElementById('type-filter')?.value;
        const difficulty = document.getElementById('difficulty-filter')?.value;
        const muscle = document.getElementById('muscle-filter')?.value;

        if (q) params.append('q', q);
        if (exercise_type) params.append('exercise_type', exercise_type);
        if (difficulty) params.append('difficulty', difficulty);
        if (muscle) params.append('muscle', muscle);

        return params;
    }

    function loadPage(page) {
        if (state.isLoading) return Promise.resolve(false);
        state.isLoading = true;

        const params = getFilterParams();
        params.append('page', page);

        return fetch(`/exercises/htmx/load-more/?${params.toString()}`, {
            headers: { 'HX-Request': 'true' }
        })
        .then(response => response.text())
        .then(html => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            const newCards = tempDiv.querySelectorAll('.exercise-item');
            const hasNextTrigger = tempDiv.querySelector('#infinite-scroll-trigger');

            const grid = document.getElementById('exercises-grid');
            if (!grid) {
                console.log('exercises-grid not found');
                return false;
            }

            if (page === 1) {
                grid.innerHTML = '';
                state.totalLoaded = 0;
            }

            newCards.forEach(card => {
                grid.appendChild(card);
                state.totalLoaded++;
            });

            const countElement = document.getElementById('exercises-count');
            if (countElement) countElement.textContent = state.totalLoaded;

            state.hasMore = hasNextTrigger !== null;
            state.isLoading = false;
            return state.hasMore;
        })
        .catch(error => {
            console.error('Error:', error);
            state.isLoading = false;
            return false;
        });
    }

    function setupInfiniteScroll() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && state.hasMore && !state.isLoading) {
                    state.currentPage++;
                    loadPage(state.currentPage);
                }
            });
        }, { threshold: 0.1, rootMargin: '100px' });

        const oldTrigger = document.getElementById('scroll-trigger');
        if (oldTrigger) oldTrigger.remove();

        const triggerDiv = document.createElement('div');
        triggerDiv.id = 'scroll-trigger';
        triggerDiv.className = 'text-center py-4';
        triggerDiv.innerHTML = '<div class="spinner-border text-success" style="display: none;" id="loading-spinner"></div>';
        const container = document.querySelector('.container');
        if (container) {
            container.appendChild(triggerDiv);
            observer.observe(triggerDiv);
        }
    }

    function refresh() {
        state.currentPage = 1;
        state.hasMore = true;
        state.isLoading = false;
        state.totalLoaded = 0;
        loadPage(1).then(() => setupInfiniteScroll());
    }

    function bindEvents() {
        const resetBtn = document.getElementById('reset-filters');
        if (resetBtn) {
            resetBtn.onclick = function() {
                const searchInput = document.getElementById('search-input');
                const typeFilter = document.getElementById('type-filter');
                const difficultyFilter = document.getElementById('difficulty-filter');
                const muscleFilter = document.getElementById('muscle-filter');

                if (searchInput) searchInput.value = '';
                if (typeFilter) typeFilter.value = '';
                if (difficultyFilter) difficultyFilter.value = '';
                if (muscleFilter) muscleFilter.value = '';
                refresh();
            };
        }

        let debounceTimer;
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.oninput = function() {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(refresh, 500);
            };
        }

        const typeFilter = document.getElementById('type-filter');
        if (typeFilter) typeFilter.onchange = refresh;

        const difficultyFilter = document.getElementById('difficulty-filter');
        if (difficultyFilter) difficultyFilter.onchange = refresh;

        const muscleFilter = document.getElementById('muscle-filter');
        if (muscleFilter) muscleFilter.onchange = refresh;
    }

    // Глобальная функция для инициализации
    window.initExerciseList = function() {
        const grid = document.getElementById('exercises-grid');
        if (!grid) {
            console.log('exercises-grid not found, waiting...');
            return false;
        }
        console.log('Initializing exercise list');
        bindEvents();
        refresh();
        return true;
    };
})();