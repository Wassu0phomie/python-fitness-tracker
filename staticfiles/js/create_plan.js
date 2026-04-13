// Глобальные переменные для create_plan
window.activeDayForSelection = null;

// Обработка выбора дней
document.querySelectorAll('.btn-check').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const dayNum = this.value;
        const dayLabel = document.querySelector(`label[for="${this.id}"]`).innerText;
        const container = document.getElementById('workout-days-container');

        if (this.checked) {
            if (container.querySelector('.text-center.py-5')) container.innerHTML = '';

            const dayBlock = document.createElement('div');
            dayBlock.id = `day-block-${dayNum}`;
            dayBlock.className = 'card mb-4 border-0 bg-light p-4 rounded-4 shadow-sm';
            dayBlock.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0 text-uppercase">${dayLabel}</h5>
                </div>
                <div class="exercise-list" id="exercise-list-${dayNum}"></div>
                <button type="button" class="btn btn-link text-dark fw-bold text-decoration-none p-0 mt-2 open-gallery-btn"
                        data-bs-toggle="modal" data-bs-target="#exerciseGallery" data-day="${dayNum}">
                    <i class="bi bi-plus-circle-fill me-2"></i>Добавить упражнение
                </button>
            `;
            container.appendChild(dayBlock);
        } else {
            const blockToRemove = document.getElementById(`day-block-${dayNum}`);
            if (blockToRemove) blockToRemove.remove();
            if (container.children.length === 0) {
                container.innerHTML = '<div class="text-center py-5 border rounded-4 border-dashed bg-light opacity-50"><i class="bi bi-calendar-check fs-1"></i><p class="mt-2">Выберите дни выше, чтобы добавить упражнения</p></div>';
            }
        }
    });
});

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.open-gallery-btn');
    if (btn) {
        window.activeDayForSelection = btn.dataset.day;
    }
});

function addExerciseToDay(id, name, img) {
    if (!window.activeDayForSelection) return;

    const listContainer = document.getElementById(`exercise-list-${window.activeDayForSelection}`);

    const row = document.createElement('div');
    row.className = 'row g-2 mb-2 align-items-center animate-fade-in';
    row.innerHTML = `
        <div class="col-md-6">
            <div class="form-control border-0 bg-white p-2 fw-bold shadow-sm" style="border-radius: 10px;">
                ${name.replace(/[<>]/g, '')}
            </div>
            <input type="hidden" name="exercises_${window.activeDayForSelection}" value="${id}">
        </div>
        <div class="col-md-2">
            <input type="number" name="sets_${window.activeDayForSelection}"
                   class="form-control border-0 p-2 shadow-sm text-center"
                   placeholder="Сеты" value="3" min="1" step="1"
                   style="border-radius: 10px;">
        </div>
        <div class="col-md-3">
            <input type="number" name="reps_${window.activeDayForSelection}"
                   class="form-control border-0 p-2 shadow-sm text-center"
                   placeholder="Повторы" value="12" min="1" step="1"
                   style="border-radius: 10px;">
        </div>
        <div class="col-md-1 text-center">
            <button type="button" class="btn text-danger p-0" onclick="this.closest('.row').remove()">
                <i class="bi bi-trash fs-5"></i>
            </button>
        </div>
    `;

    listContainer.appendChild(row);

    const modalElement = document.getElementById('exerciseGallery');
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) modal.hide();
}

window.currentMuscleFilter = 'all';

function applyFilters() {
    const searchQuery = document.getElementById('modalSearch').value.toLowerCase();

    document.querySelectorAll('.modal-ex-card').forEach(card => {
        const name = card.dataset.name;
        const muscles = card.dataset.muscles.trim().split(' ');

        const matchesSearch = name.includes(searchQuery);
        const matchesMuscle = (window.currentMuscleFilter === 'all' || muscles.includes(window.currentMuscleFilter));

        if (matchesSearch && matchesMuscle) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

document.getElementById('modalSearch').addEventListener('input', applyFilters);

document.querySelectorAll('.filter-muscle-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-muscle-btn').forEach(b => {
            b.classList.remove('btn-dark', 'active');
            b.classList.add('btn-outline-secondary');
        });
        this.classList.remove('btn-outline-secondary');
        this.classList.add('btn-dark', 'active');

        window.currentMuscleFilter = this.dataset.muscle;
        applyFilters();
    });
});

document.getElementById('planForm').addEventListener('submit', function(e) {
    const selectedDayCheckboxes = document.querySelectorAll('.btn-check:checked');

    if (selectedDayCheckboxes.length === 0) {
        e.preventDefault();
        alert('Пожалуйста, выберите хотя бы один день недели!');
        return;
    }

    let totalExercises = 0;
    selectedDayCheckboxes.forEach(checkbox => {
        const dayNum = checkbox.value;
        const exercisesInDay = document.querySelectorAll(`#exercise-list-${dayNum} input[name^="exercises_"]`);
        totalExercises += exercisesInDay.length;
    });

    if (totalExercises === 0) {
        e.preventDefault();
        alert('Добавьте хотя бы одно упражнение в выбранные дни!');
        return;
    }
});

const exerciseModal = document.getElementById('exerciseGallery');
if (exerciseModal) {
    exerciseModal.addEventListener('hidden.bs.modal', function() {
        const searchInput = document.getElementById('modalSearch');
        if (searchInput) {
            searchInput.value = '';
        }

        window.currentMuscleFilter = 'all';

        document.querySelectorAll('.filter-muscle-btn').forEach(btn => {
            btn.classList.remove('btn-dark', 'active');
            btn.classList.add('btn-outline-secondary');
        });

        const allButton = document.querySelector('.filter-muscle-btn[data-muscle="all"]');
        if (allButton) {
            allButton.classList.remove('btn-outline-secondary');
            allButton.classList.add('btn-dark', 'active');
        }

        document.querySelectorAll('.modal-ex-card').forEach(card => {
            card.style.display = 'block';
        });
    });
}