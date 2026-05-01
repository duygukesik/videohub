// ====== State ======
let videos = JSON.parse(localStorage.getItem('videohub_v2')) || [];
let categories = JSON.parse(localStorage.getItem('videohub_categories')) || ['Music', 'Education', 'Gaming', 'Tech', 'Other'];

// ====== DOM Elements ======
const DOMElements = {
    grid: document.getElementById('videoGrid'),
    emptyState: document.getElementById('emptyState'),
    search: document.getElementById('searchInput'),
    filter: document.getElementById('categoryFilter'),
    addBtn: document.getElementById('addBtn'),
    addModal: document.getElementById('addModal'),
    addForm: document.getElementById('addForm'),
    closeAddBtn: document.getElementById('closeAddBtn'),
    playerModal: document.getElementById('playerModal'),
    playerWrapper: document.getElementById('playerWrapper'),
    closePlayerBtn: document.getElementById('closePlayerBtn'),
    addCategoryBtn: document.getElementById('addCategoryBtn'),
    videoCategory: document.getElementById('videoCategory')
};

// ====== Utilities ======
const extractYouTubeID = (url) => {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/i;
    const match = url.match(regex);
    return match ? match[1] : null;
};

const saveState = () => {
    localStorage.setItem('videohub_v2', JSON.stringify(videos));
};

const saveCategories = () => {
    localStorage.setItem('videohub_categories', JSON.stringify(categories));
};

const escapeHTML = (str) => {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag])
    );
};

// ====== Rendering ======
const renderCategories = () => {
    DOMElements.filter.innerHTML = '<option value="All">All Categories</option>';
    DOMElements.videoCategory.innerHTML = '';
    
    categories.forEach(cat => {
        const escapedCat = escapeHTML(cat);
        DOMElements.filter.innerHTML += `<option value="${escapedCat}">${escapedCat}</option>`;
        DOMElements.videoCategory.innerHTML += `<option value="${escapedCat}">${escapedCat}</option>`;
    });
};

const renderVideos = () => {
    const searchTerm = DOMElements.search.value.toLowerCase();
    const category = DOMElements.filter.value;

    const filtered = videos.filter(v => {
        const matchesSearch = v.title.toLowerCase().includes(searchTerm);
        const matchesCat = category === 'All' || v.category === category;
        return matchesSearch && matchesCat;
    });

    DOMElements.grid.innerHTML = '';

    if (filtered.length === 0) {
        DOMElements.emptyState.classList.remove('hidden');
    } else {
        DOMElements.emptyState.classList.add('hidden');
        
        const fragment = document.createDocumentFragment();
        filtered.forEach(video => {
            const card = document.createElement('div');
            card.className = 'video-card';
            card.innerHTML = `
                <div class="card-thumb" onclick="playVideo('${video.ytId}')">
                    <img src="https://img.youtube.com/vi/${video.ytId}/maxresdefault.jpg" 
                         onerror="this.onerror=null; this.src='https://img.youtube.com/vi/${video.ytId}/hqdefault.jpg'" 
                         alt="${escapeHTML(video.title)}">
                    <div class="play-overlay">
                        <div class="play-btn-visual">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <h3 class="card-title">${escapeHTML(video.title)}</h3>
                    <div class="card-meta">
                        <span class="badge">${escapeHTML(video.category)}</span>
                        <button class="delete-btn" onclick="deleteVideo('${video.id}')" title="Remove video">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18m-2 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                        </button>
                    </div>
                </div>
            `;
            fragment.appendChild(card);
        });
        DOMElements.grid.appendChild(fragment);
    }
};

// ====== Actions ======
const addVideo = (e) => {
    e.preventDefault();
    const title = document.getElementById('videoTitle').value.trim();
    const url = document.getElementById('videoUrl').value.trim();
    const category = document.getElementById('videoCategory').value;

    const ytId = extractYouTubeID(url);
    if (!ytId) {
        alert("Please enter a valid YouTube URL (e.g. https://www.youtube.com/watch?v=...)");
        return;
    }

    const newVideo = {
        id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        title,
        ytId,
        category,
        addedAt: Date.now()
    };

    videos.unshift(newVideo);
    saveState();
    renderVideos();
    
    closeModal(DOMElements.addModal);
    DOMElements.addForm.reset();
};

window.deleteVideo = (id) => {
    if (confirm("Are you sure you want to remove this video from your collection?")) {
        videos = videos.filter(v => v.id !== id);
        saveState();
        renderVideos();
    }
};

window.playVideo = (ytId) => {
    DOMElements.playerWrapper.innerHTML = `
        <iframe 
            src="https://www.youtube.com/embed/${ytId}?autoplay=1&rel=0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
        </iframe>
    `;
    openModal(DOMElements.playerModal);
};

const addCategory = () => {
    const newCat = prompt("Enter new category name:");
    if (newCat && newCat.trim() !== '') {
        const trimmed = newCat.trim();
        if (!categories.includes(trimmed)) {
            categories.push(trimmed);
            saveCategories();
            renderCategories();
        } else {
            alert("Category already exists!");
        }
    }
};

// ====== Modals ======
const openModal = (modal) => modal.classList.remove('hidden');
const closeModal = (modal) => {
    modal.classList.add('hidden');
    if (modal === DOMElements.playerModal) {
        DOMElements.playerWrapper.innerHTML = ''; // Stop video playback
    }
};

// ====== Event Listeners ======
DOMElements.addBtn.addEventListener('click', () => openModal(DOMElements.addModal));
DOMElements.closeAddBtn.addEventListener('click', () => closeModal(DOMElements.addModal));
DOMElements.closePlayerBtn.addEventListener('click', () => closeModal(DOMElements.playerModal));
DOMElements.addForm.addEventListener('submit', addVideo);
DOMElements.search.addEventListener('input', renderVideos);
DOMElements.filter.addEventListener('change', renderVideos);
DOMElements.addCategoryBtn.addEventListener('click', addCategory);

// Close modals on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        closeModal(e.target);
    }
});

// ====== Init ======
renderCategories();
renderVideos();
