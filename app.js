// Kids Pension Comparator Application Logic

// Application State
let activeFilters = new Set();
let compareList = [];
const MAX_COMPARE = 4;

// DOM Elements
const pensionsGrid = document.getElementById("pensionsGrid");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");
const filterBtns = document.querySelectorAll(".filter-btn");
const resetFiltersBtn = document.getElementById("resetFilters");
const pensionCount = document.getElementById("pensionCount");
const emptyState = document.getElementById("emptyState");

const compareDrawer = document.getElementById("compareDrawer");
const compareDrawerItems = document.getElementById("compareDrawerItems");
const compareCount = document.getElementById("compareCount");
const compareSubmitBtn = document.getElementById("compareSubmitBtn");
const compareClearBtn = document.getElementById("compareClearBtn");

const detailModal = document.getElementById("detailModal");
const detailModalBody = document.getElementById("detailModalBody");
const closeDetailModal = document.getElementById("closeDetailModal");

const compareModal = document.getElementById("compareModal");
const compareTable = document.getElementById("compareTable");
const closeCompareModal = document.getElementById("closeCompareModal");

// 1. Initial Render
document.addEventListener("DOMContentLoaded", () => {
    renderPensions();
    setupEventListeners();
});

// 2. Render Pensions Grid
function renderPensions() {
    const query = searchInput.value.toLowerCase().trim();
    const sortBy = sortSelect.value;
    
    // Filter
    let filtered = pensionsData.filter(pension => {
        // Search text matching
        const matchesSearch = pension.name.toLowerCase().includes(query) || 
                              pension.metadata.링크.toLowerCase().includes(query) || 
                              pension.memo.toLowerCase().includes(query) ||
                              (pension.filename && pension.filename.toLowerCase().includes(query));
                              
        if (!matchesSearch) return false;
        
        // 5 Core Criteria Filters
        for (let criterion of activeFilters) {
            const val = pension.metadata;
            if (criterion === "온수풀") {
                if (val.온수풀.includes("아님") || val.온수풀.includes("아니오")) return false;
            } else if (criterion === "방개수") {
                if (val.방개수_숫자 < 5) return false;
            } else if (criterion === "금액") {
                if (val.금액숫자 > 100) return false;
            } else if (criterion === "키즈풀빌라") {
                if (val.키즈풀빌라.includes("아니오") || val.키즈풀빌라.includes("아님")) return false;
            } else if (criterion === "대중교통") {
                if (!val.대중교통.includes("가능")) return false;
            }
        }
        return true;
    });

    // Sort
    if (sortBy === "rating") {
        filtered.sort((a, b) => b.metadata.평점 - a.metadata.평점);
    } else if (sortBy === "price-asc") {
        filtered.sort((a, b) => a.metadata.금액숫자 - b.metadata.금액숫자);
    } else if (sortBy === "price-desc") {
        filtered.sort((a, b) => b.metadata.금액숫자 - a.metadata.금액숫자);
    } else if (sortBy === "rooms") {
        filtered.sort((a, b) => b.metadata.방개수_숫자 - a.metadata.방개수_숫자);
    }

    // Render Count
    pensionCount.textContent = `총 ${filtered.length}개의 후보 매칭됨`;

    // Render Grid
    pensionsGrid.innerHTML = "";
    if (filtered.length === 0) {
        emptyState.classList.remove("hidden");
        return;
    }
    emptyState.classList.add("hidden");

    filtered.forEach(pension => {
        const isChecked = compareList.some(item => item.id === pension.id);
        const card = document.createElement("div");
        card.className = "pension-card";
        
        // Parse metadata badges
        const hasPool = !(pension.metadata.온수풀.includes("아님") || pension.metadata.온수풀.includes("아니오"));
        const hasRooms = pension.metadata.방개수_숫자 >= 5;
        const isCheap = pension.metadata.금액숫자 <= 100;
        const isKids = !(pension.metadata.키즈풀빌라.includes("아니오") || pension.metadata.키즈풀빌라.includes("아님"));
        const hasTransit = pension.metadata.대중교통.includes("가능");

        card.innerHTML = `
            <div class="card-img-wrapper">
                <img class="card-img" src="${pension.cover_image}" alt="${pension.name}" onerror="this.src='assets/placeholder.jpg'">
                <div class="card-rating-badge">
                    <i class="fa-solid fa-star"></i> ${pension.metadata.평점}
                </div>
                <!-- 5대 기준 퀵 패스 배지 -->
                <div class="card-badges">
                    <div class="criterion-badge ${hasPool ? 'active' : ''}" title="온수풀: ${pension.metadata.온수풀}">🏊</div>
                    <div class="criterion-badge ${hasRooms ? 'active' : ''}" title="방 개수: ${pension.metadata.방개수}">🛏️</div>
                    <div class="criterion-badge ${isCheap ? 'active' : (pension.metadata.금액숫자 > 100 ? 'warning' : '')}" title="금액: ${pension.metadata.금액}">💵</div>
                    <div class="criterion-badge ${isKids ? 'active' : ''}" title="키즈풀빌라: ${pension.metadata.키즈풀빌라}">🧸</div>
                    <div class="criterion-badge ${hasTransit ? 'active' : ''}" title="대중교통: ${pension.metadata.대중교통}">🚇</div>
                </div>
            </div>
            <div class="card-info">
                <h3 class="card-title">${pension.name}</h3>
                <div class="card-meta-row">
                    <span class="card-meta-item"><i class="fa-solid fa-bed"></i> 방 ${pension.metadata.방개수_숫자}개</span>
                    <span class="card-meta-item"><i class="fa-solid fa-won-sign"></i> ${pension.metadata.금액숫자 > 100 ? pension.metadata.금액숫자 + '만+' : pension.metadata.금액숫자 + '만'}</span>
                </div>
                <div class="card-features">
                    <div class="feature-list-title">핵심 시설</div>
                    <ul>
                        ${pension.kids_facilities.slice(0, 3).map(f => `<li><i class="fa-solid fa-check"></i> ${f}</li>`).join('')}
                    </ul>
                </div>
                ${pension.memo ? `<div class="card-memo">${pension.memo}</div>` : ''}
                <div class="card-actions">
                    <input type="checkbox" class="compare-checkbox-input" id="comp_${pension.id}" ${isChecked ? 'checked' : ''}>
                    <label class="compare-checkbox-label" for="comp_${pension.id}" data-pension-id="${pension.id}">
                        <i class="fa-solid fa-code-compare"></i> 비교담기
                    </label>
                    <button class="primary-btn view-detail-btn" data-pension-id="${pension.id}">상세 노트</button>
                </div>
            </div>
        `;
        pensionsGrid.appendChild(card);
    });

    // Rebind events to dynamically created buttons
    bindCardEvents();
}

// 3. Event Listeners Setup
function setupEventListeners() {
    // Search
    searchInput.addEventListener("input", renderPensions);
    
    // Sort
    sortSelect.addEventListener("change", renderPensions);

    // 5대 기준 필터 토글
    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const criterion = btn.getAttribute("data-criterion");
            if (activeFilters.has(criterion)) {
                activeFilters.delete(criterion);
                btn.classList.remove("active");
            } else {
                activeFilters.add(criterion);
                btn.classList.add("active");
            }
            renderPensions();
        });
    });

    // Reset Filters
    resetFiltersBtn.addEventListener("click", () => {
        activeFilters.clear();
        filterBtns.forEach(btn => btn.classList.remove("active"));
        searchInput.value = "";
        sortSelect.value = "default";
        renderPensions();
    });

    // Compare Drawer Actions
    compareClearBtn.addEventListener("click", clearCompareList);
    compareSubmitBtn.addEventListener("click", openCompareModal);

    // Close Modals
    closeDetailModal.addEventListener("click", () => detailModal.classList.remove("open"));
    closeCompareModal.addEventListener("click", () => compareModal.classList.remove("open"));
    
    // Close modal on background click
    window.addEventListener("click", (e) => {
        if (e.target === detailModal) detailModal.classList.remove("open");
        if (e.target === compareModal) compareModal.classList.remove("open");
    });
}

// 4. Bind Card Interactivity
function bindCardEvents() {
    // Checkbox compare clicks
    const labels = document.querySelectorAll(".compare-checkbox-label");
    labels.forEach(label => {
        label.addEventListener("click", (e) => {
            e.preventDefault(); // Handle manually to avoid double fires
            const checkbox = document.getElementById(label.getAttribute("for"));
            const pensionId = label.getAttribute("data-pension-id");
            const pension = pensionsData.find(p => p.id === pensionId);

            if (checkbox.checked) {
                // Remove
                checkbox.checked = false;
                compareList = compareList.filter(item => item.id !== pensionId);
            } else {
                // Add
                if (compareList.length >= MAX_COMPARE) {
                    alert(`비교는 최대 ${MAX_COMPARE}개까지만 가능합니다!`);
                    return;
                }
                checkbox.checked = true;
                compareList.push(pension);
            }
            updateCompareDrawer();
        });
    });

    // Detail Button clicks
    const detailBtns = document.querySelectorAll(".view-detail-btn");
    detailBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const pensionId = btn.getAttribute("data-pension-id");
            const pension = pensionsData.find(p => p.id === pensionId);
            openDetailModal(pension);
        });
    });
}

// 5. Update Compare Drawer state
function updateCompareDrawer() {
    compareCount.textContent = compareList.length;
    compareDrawerItems.innerHTML = "";

    if (compareList.length > 0) {
        compareDrawer.classList.add("open");
        compareSubmitBtn.disabled = compareList.length < 2; // Need at least 2 items to compare

        compareList.forEach(pension => {
            const item = document.createElement("div");
            item.className = "drawer-item";
            item.innerHTML = `
                <img src="${pension.cover_image}" alt="${pension.name}">
                <span>${pension.name}</span>
                <button class="drawer-item-remove" data-id="${pension.id}">&times;</button>
            `;
            // Remove handler inside drawer
            item.querySelector(".drawer-item-remove").addEventListener("click", () => {
                compareList = compareList.filter(p => p.id !== pension.id);
                updateCompareDrawer();
                // Sync grid check
                const checkbox = document.getElementById(`comp_${pension.id}`);
                if (checkbox) checkbox.checked = false;
            });
            compareDrawerItems.appendChild(item);
        });
    } else {
        compareDrawer.classList.remove("open");
    }
}

// Clear all compare selections
function clearCompareList() {
    compareList = [];
    updateCompareDrawer();
    // Deselect all grid checkboxes
    document.querySelectorAll(".compare-checkbox-input").forEach(cb => cb.checked = false);
}

// 6. Open Detail Modal & Initialize Carousel
function openDetailModal(pension) {
    // Generate carousel HTML
    let carouselHtml = "";
    if (pension.images && pension.images.length > 0) {
        carouselHtml = `
            <div class="carousel">
                <div class="carousel-track" id="carouselTrack">
                    ${pension.images.map(img => `
                        <div class="carousel-slide">
                            <img src="${img}" alt="${pension.name}" onerror="this.src='assets/placeholder.jpg'">
                        </div>
                    `).join('')}
                </div>
                ${pension.images.length > 1 ? `
                    <button class="carousel-btn carousel-btn-prev" id="carouselPrev"><i class="fa-solid fa-chevron-left"></i></button>
                    <button class="carousel-btn carousel-btn-next" id="carouselNext"><i class="fa-solid fa-chevron-right"></i></button>
                    <div class="carousel-dots" id="carouselDots">
                        ${pension.images.map((_, i) => `<span class="carousel-dot ${i === 0 ? 'active' : ''}" data-index="${i}"></span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Standard evaluations check
    const hasPool = !(pension.metadata.온수풀.includes("아님") || pension.metadata.온수풀.includes("아니오"));
    const hasRooms = pension.metadata.방개수_숫자 >= 5;
    const isCheap = pension.metadata.금액숫자 <= 100;
    const isKids = !(pension.metadata.키즈풀빌라.includes("아니오") || pension.metadata.키즈풀빌라.includes("아님"));
    const hasTransit = pension.metadata.대중교통.includes("가능");

    // Populate modal body
    detailModalBody.innerHTML = `
        <div class="detail-header">
            <h2 class="detail-title">${pension.name}</h2>
            <div class="detail-location"><i class="fa-solid fa-location-dot"></i> ${pension.filename.replace('.md', '')}</div>
        </div>

        ${carouselHtml}

        <div class="detail-grid">
            <!-- 5대 기준 충족표 -->
            <div class="detail-meta-card">
                <h3><i class="fa-solid fa-clipboard-check"></i> 5대 평가 핵심 대조</h3>
                <table class="detail-meta-table">
                    <tr>
                        <td class="label-col">🏊 온수풀</td>
                        <td class="value-col ${hasPool ? 'success' : 'alert'}">${pension.metadata.온수풀}</td>
                    </tr>
                    <tr>
                        <td class="label-col">🛏️ 방 개수</td>
                        <td class="value-col ${hasRooms ? 'success' : 'alert'}">${pension.metadata.방개수}</td>
                    </tr>
                    <tr>
                        <td class="label-col">💵 숙박 금액</td>
                        <td class="value-col ${isCheap ? 'success' : 'alert'}">${pension.metadata.금액}</td>
                    </tr>
                    <tr>
                        <td class="label-col">🧸 키즈풀빌라</td>
                        <td class="value-col ${isKids ? 'success' : 'alert'}">${pension.metadata.키즈풀빌라}</td>
                    </tr>
                    <tr>
                        <td class="label-col">🚇 대중교통</td>
                        <td class="value-col ${hasTransit ? 'success' : 'alert'}">${pension.metadata.대중교통}</td>
                    </tr>
                </table>
            </div>
            
            <!-- 평점 및 링크 -->
            <div class="detail-meta-card">
                <h3><i class="fa-solid fa-circle-info"></i> 일반 정보</h3>
                <table class="detail-meta-table">
                    <tr>
                        <td class="label-col">⭐ 만족 평점</td>
                        <td class="value-col" style="color:var(--color-warning);">${pension.metadata.평점} / 5.0</td>
                    </tr>
                    <tr>
                        <td class="label-col">📁 매칭 노트</td>
                        <td class="value-col" style="font-weight:400;">${pension.filename}</td>
                    </tr>
                    <tr>
                        <td class="label-col">🔗 예약 사이트</td>
                        <td class="value-col"><a href="${pension.metadata.링크}" target="_blank" style="color:var(--color-info); text-decoration:none;"><i class="fa-solid fa-arrow-up-right-from-square"></i> 예약 사이트 가기</a></td>
                    </tr>
                </table>
            </div>
        </div>

        ${pension.memo ? `
            <div class="detail-memo-box">
                <h3><i class="fa-solid fa-pencil"></i> 옵시디언 개별 메모</h3>
                <p>${pension.memo}</p>
            </div>
        ` : ''}

        <!-- 장단점 대조 -->
        <div class="detail-grid">
            <div class="detail-content-card">
                <h3 style="border-color:var(--color-success);"><i class="fa-solid fa-thumbs-up" style="color:var(--color-success)"></i> 이 펜션의 장점</h3>
                <ul>
                    ${pension.pros.length > 0 ? pension.pros.map(p => `<li class="pro"><i class="fa-solid fa-plus-circle"></i> <span>${p}</span></li>`).join('') : '<li style="color:var(--text-muted)">적혀있는 장점이 없습니다.</li>'}
                </ul>
            </div>
            <div class="detail-content-card">
                <h3 style="border-color:var(--color-danger);"><i class="fa-solid fa-thumbs-down" style="color:var(--color-danger)"></i> 이 펜션의 단점</h3>
                <ul>
                    ${pension.cons.length > 0 ? pension.cons.map(c => `<li class="con"><i class="fa-solid fa-minus-circle"></i> <span>${c}</span></li>`).join('') : '<li style="color:var(--text-muted)">적혀있는 단점이 없습니다.</li>'}
                </ul>
            </div>
        </div>

        <!-- 전체 시설 리스트 -->
        <div class="detail-content-card" style="margin-bottom:10px;">
            <h3><i class="fa-solid fa-wand-magic-sparkles"></i> 전체 구비 및 놀이 시설</h3>
            <div class="detail-grid" style="border:none; padding:0; margin:0;">
                <div>
                    <h4 style="font-size:0.9rem; color:var(--text-muted); margin-bottom:8px;">🧸 키즈 놀이시설</h4>
                    <ul>
                        ${pension.kids_facilities.map(kf => `<li class="facility"><i class="fa-solid fa-circle-dot"></i> <span>${kf}</span></li>`).join('')}
                    </ul>
                </div>
                <div>
                    <h4 style="font-size:0.9rem; color:var(--text-muted); margin-bottom:8px;">🏡 일반 가전 및 비품</h4>
                    <ul>
                        ${pension.general_facilities.map(gf => `<li class="facility"><i class="fa-solid fa-circle-chevron-right"></i> <span>${gf}</span></li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;

    detailModal.classList.add("open");

    // Initialize carousel JS logic if multiple images
    if (pension.images && pension.images.length > 1) {
        initCarousel();
    }
}

// 7. Image Slider (Carousel) Logic inside Modal
function initCarousel() {
    const track = document.getElementById("carouselTrack");
    const prevBtn = document.getElementById("carouselPrev");
    const nextBtn = document.getElementById("carouselNext");
    const dotsContainer = document.getElementById("carouselDots");
    const dots = Array.from(dotsContainer.children);
    
    let currentIndex = 0;
    const totalSlides = dots.length;

    function updateCarousel(index) {
        if (index < 0) index = totalSlides - 1;
        if (index >= totalSlides) index = 0;
        
        currentIndex = index;
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        // Dots sync
        dots.forEach((dot, idx) => {
            if (idx === currentIndex) {
                dot.classList.add("active");
            } else {
                dot.classList.remove("active");
            }
        });
    }

    prevBtn.addEventListener("click", () => updateCarousel(currentIndex - 1));
    nextBtn.addEventListener("click", () => updateCarousel(currentIndex + 1));
    
    dots.forEach(dot => {
        dot.addEventListener("click", () => {
            const index = parseInt(dot.getAttribute("data-index"));
            updateCarousel(index);
        });
    });
}

// 8. Open Side-by-Side Comparison Table Modal
function openCompareModal() {
    if (compareList.length < 2) return;

    compareTable.innerHTML = "";

    // 1. Header Row (Images & Names)
    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>비교 항목</th>
        ${compareList.map(p => {
            const hasPool = !(p.metadata.온수풀.includes("아님") || p.metadata.온수풀.includes("아니오"));
            const hasRooms = p.metadata.방개수_숫자 >= 5;
            const isCheap = p.metadata.금액숫자 <= 100;
            const isKids = !(p.metadata.키즈풀빌라.includes("아니오") || p.metadata.키즈풀빌라.includes("아님"));
            const hasTransit = p.metadata.대중교통.includes("가능");

            return `
                <th class="compare-pension-header">
                    <h4>${p.name}</h4>
                    <img class="compare-pension-img" src="${p.cover_image}" alt="${p.name}" onerror="this.src='assets/placeholder.jpg'">
                    <div class="compare-badge-container">
                        <span class="criterion-badge ${hasPool ? 'active' : ''}">🏊</span>
                        <span class="criterion-badge ${hasRooms ? 'active' : ''}">🛏️</span>
                        <span class="criterion-badge ${isCheap ? 'active' : (p.metadata.금액숫자 > 100 ? 'warning' : '')}">💵</span>
                        <span class="criterion-badge ${isKids ? 'active' : ''}">🧸</span>
                        <span class="criterion-badge ${hasTransit ? 'active' : ''}">🚇</span>
                    </div>
                </th>
            `;
        }).join('')}
    `;
    compareTable.appendChild(headerRow);

    // Dynamic Comparison Rows Definition
    const rows = [
        {
            label: "⭐ 만족도 평점",
            parse: p => `<strong style="color:var(--color-warning); font-size:1.15rem;">${p.metadata.평점}</strong> / 5.0`
        },
        {
            label: "🏊 온수풀",
            parse: p => {
                const has = !(p.metadata.온수풀.includes("아님") || p.metadata.온수풀.includes("아니오"));
                return `<td class="meta-val ${has ? 'success' : 'danger'}">${p.metadata.온수풀}</td>`;
            },
            customTd: true
        },
        {
            label: "🛏️ 방 개수",
            parse: p => {
                const has = p.metadata.방개수_숫자 >= 5;
                return `<td class="meta-val ${has ? 'success' : 'warning'}">${p.metadata.방개수}</td>`;
            },
            customTd: true
        },
        {
            label: "💵 숙박 금액",
            parse: p => {
                const cheap = p.metadata.금액숫자 <= 100;
                return `<td class="meta-val ${cheap ? 'success' : 'danger'}">${p.metadata.금액}</td>`;
            },
            customTd: true
        },
        {
            label: "🧸 키즈풀빌라",
            parse: p => {
                const has = !(p.metadata.키즈풀빌라.includes("아니오") || p.metadata.키즈풀빌라.includes("아님"));
                return `<td class="meta-val ${has ? 'success' : 'danger'}">${p.metadata.키즈풀빌라}</td>`;
            },
            customTd: true
        },
        {
            label: "🚇 대중교통",
            parse: p => {
                const has = p.metadata.대중교통.includes("가능");
                return `<td class="meta-val ${has ? 'success' : 'danger'}">${p.metadata.대중교통}</td>`;
            },
            customTd: true
        },
        {
            label: "🧸 핵심 키즈 시설",
            parse: p => `
                <ul class="table-bullet-list">
                    ${p.kids_facilities.map(kf => `<li><i class="fa-solid fa-circle-dot" style="color:var(--color-info)"></i> <span>${kf}</span></li>`).join('')}
                </ul>
            `
        },
        {
            label: "🏡 일반 시설 & 가전",
            parse: p => `
                <ul class="table-bullet-list">
                    ${p.general_facilities.slice(0, 5).map(gf => `<li><i class="fa-solid fa-angle-right" style="color:var(--text-muted)"></i> <span>${gf}</span></li>`).join('')}
                </ul>
            `
        },
        {
            label: "👍 펜션 장점",
            parse: p => `
                <ul class="table-bullet-list">
                    ${p.pros.map(pro => `<li class="pro"><i class="fa-solid fa-circle-plus"></i> <span>${pro}</span></li>`).join('')}
                </ul>
            `
        },
        {
            label: "👎 펜션 단점",
            parse: p => `
                <ul class="table-bullet-list">
                    ${p.cons.map(con => `<li class="con"><i class="fa-solid fa-circle-minus"></i> <span>${con}</span></li>`).join('')}
                </ul>
            `
        },
        {
            label: "✍️ 개별 평가 메모",
            parse: p => `<p style="font-style:italic; font-size:0.83rem; color:var(--text-muted);">${p.memo || '적어둔 메모가 없습니다.'}</p>`
        }
    ];

    // Build Table Rows
    rows.forEach(rowData => {
        const tr = document.createElement("tr");
        if (rowData.customTd) {
            tr.innerHTML = `
                <td>${rowData.label}</td>
                ${compareList.map(p => rowData.parse(p)).join('')}
            `;
        } else {
            tr.innerHTML = `
                <td>${rowData.label}</td>
                ${compareList.map(p => `<td>${rowData.parse(p)}</td>`).join('')}
            `;
        }
        compareTable.appendChild(tr);
    });

    compareModal.classList.add("open");
}
