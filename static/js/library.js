


const getTotalPages = () => {
    return Math.ceil(ITEMS_FILTERED.length / ITEMS_PER_PAGE);
};

const getTrimmedText = (text, max_lenght) => {
    if ( text.length > max_lenght ) { return text.substring(0, max_lenght).trimEnd() + '...'; }
    else { return text; }
};

const getModels = (model) => {
    return model.map(actor => `<small class="text-primary" onclick="searchByModel('${actor}')" style="cursor:pointer;">${toTitleCase(actor)}</small>`);
};


const createCard = (item) => {
    var itemTitle       = item.title ? item.title : ``;
    var itemPoster      = `static/` + (item.poster ? item.poster : `img/img_404.jpg`);
    var itemIcon      = `static/` + (item.icon ? item.icon : `img/icon.png`);
    var div = document.createElement('div');
    div.setAttribute('class', 'col');
    div.innerHTML = `
        <!-- <a class="btn position-absolute top-0 end-0 m-2 p-1" onclick="actionFavorite(this, ${item.id})"><i class="${item.favorite == 1 ? `bi bi-bookmark-fill` : `bi bi-bookmark` }"></i></a> -->
        <div id="parent" class="ratio ratio-16x9 cover border" style="background-image:url('${item.poster_path}');" onmouseenter="toggleVisible('on')" onmouseleave="toggleVisible('off')">
            <a href="${item.url}" target="_blank" class="w-100 h-100 p-2 d-flex justify-content-center align-items-center d-none">
                <p class="text-center">${toTitleCase(getTrimmedText(itemTitle, 60))}</p>
            </a>
        </div>
        <div class="btn-group mr-2 w-100 " role="group">
            <button class="btn app-btn rounded-top-0" onclick="actionDelete('${item.id}')" data-bs-toggle="tooltip-lib" data-bs-title="Delete"><i class="bi bi-trash"></i></button>
            <button class="btn app-btn rounded-top-0" onclick="actionFetch('${item.url}')" data-bs-toggle="tooltip-lib" data-bs-title="Re-Link"><i class="bi bi-link"></i></button>
            <button class="btn app-btn rounded-top-0" onclick="actionEdit('${item.id}')" data-bs-toggle="tooltip-lib" data-bs-title="Edit"><i class="bi bi-pencil-square"></i></button>
            <button class="btn app-btn rounded-top-0" onclick="actionGoTo('${item.url}')" data-bs-toggle="tooltip-lib" data-bs-title="Go to URL"><i class="bi bi-play-fill"></i></button>
        </div>
        <div>
            <p class="text-start"><small><img src="${item.icon_path}" width="16"> <a href="${item.schema}://${item.host}" target="_blank" class="text-decoration-none">${item.host}</small></a></p>
            <p class="text-center"><small>${toTitleCase(getTrimmedText(itemTitle, 50))}</small></p>
            <p class="text-center"><small>${getModels(item.models.split(',')).join(' | ')}</small></p>
            
        </div>
    `;
    return div;
}

const createPaginationButton = (buttonNumber) => {
    const button = document.createElement('button');
    button.setAttribute('class', 'btn app-btn');
    if (buttonNumber === PAGE_CURRENT) {
        button.setAttribute('disabled', true);
    }
    button.setAttribute('onclick', `updatePagination(${buttonNumber})`)
    button.textContent = buttonNumber;
    return button;
}

function createPaginationEllipsis() {
    const button = document.createElement('button');
    button.setAttribute('class', 'btn border-0');
    button.setAttribute('disabled', true);
    button.textContent = `…`;
    return button;
}

function createPagination() {
    PAGE_CURRENT = PAGE_CURRENT > PAGES_TOTAL ? PAGES_TOTAL : PAGE_CURRENT;
    const paginationTop = document.getElementById('paginationTop');
    const paginationBottom = document.getElementById('paginationBottom');
    paginationTop.innerHTML = '';
    paginationBottom.innerHTML = '';
    let elipsisSet = false;
    for( i=1; i <=PAGES_TOTAL; i++ ){
        if (
            PAGES_TOTAL <= 5
            || i == 1
            || i == PAGE_CURRENT
            || i == PAGE_CURRENT + 1
            || i == PAGE_CURRENT - 1
            || i == PAGES_TOTAL
        ) {
            paginationTop.appendChild(createPaginationButton(i));
            elipsisSet = false;
        } else {
            if ( elipsisSet == false ){
                paginationTop.appendChild(createPaginationEllipsis());
                elipsisSet = true;
            }
        }
    }
    paginationBottom.innerHTML = paginationTop.innerHTML;
}

function createModelsSelection() {
    var modelList = []
    var filterModels = document.getElementById('filter-model')
    ITEMS_ALL.slice().forEach( item => {
        var itemModels = item.models ? item.models : ``;
        if (itemModels.includes(',')) {
            modelList = modelList.concat(itemModels.split(','));
        } else {
            modelList.push(itemModels);
        }
    })
    modelList = Array.from(new Set(modelList));
    modelList = modelList.filter(function(actor) { return actor.trim() !== ""; });
    modelList.sort();
    modelList = modelList.map(toTitleCase);
    modelList.forEach( actorName => {
        filterModels.innerHTML += `<option value="${actorName.toLowerCase()}">${actorName}</option>`;
    } );
}

function displayItems() {
    const itemsContainer = document.getElementById('items');
    itemsContainer.innerHTML = '';
    if (!ITEMS_FILTERED || ITEMS_FILTERED.length == 0) {
        console.log("Filtered data is not available.");
        return;
    }
    const startIndex = (PAGE_CURRENT - 1) * ITEMS_PER_PAGE;
    const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, ITEMS_FILTERED.length);
    const itemsToDisplay = ITEMS_FILTERED.slice(startIndex, endIndex);
    itemsToDisplay.forEach( item => {
        var div = createCard(item);
        itemsContainer.appendChild(div);
    });
    const tooltipItems = document.querySelectorAll('[data-bs-toggle="tooltip-lib"]')
    const tooltipItemLists = [...tooltipItems].map(element => new bootstrap.Tooltip(element))
}

function updatePagination(pageNumber) {
    PAGE_CURRENT = pageNumber;
    displayItems();
    createPagination();
}

async function loadItems(url) {
    const response = await fetch(url);
    ITEMS_ALL = await response.json();
    ITEMS_ALL = ITEMS_ALL.map(item => ({
        ...item,
        title: item.title.toLowerCase(),
        tags: item.tags.toLowerCase(),
        description: item.description.toLowerCase(),
        model: item.models.toLowerCase(),
        host: item.host.toLowerCase()
      }));
    ITEMS_FILTERED = ITEMS_ALL;
    PAGES_TOTAL = getTotalPages();
    updatePagination(PAGE_CURRENT);
    createModelsSelection();
}

function filterItems() {
    let filterModels = document.getElementById('filter-model').value.toLowerCase();
    let filterInput = document.getElementById('filter-input').value.toLowerCase();
    ITEMS_FILTERED = ITEMS_ALL.filter(item => item.model.includes(filterModels));
    ITEMS_FILTERED = ITEMS_FILTERED.filter(item =>
        item.tags.includes(filterInput) ||
        item.title.includes(filterInput) ||
        item.host.includes(filterInput)
    );
    PAGES_TOTAL = getTotalPages();
    updatePagination(1);
}

let timeoutId;
document.getElementById('filter-input').addEventListener('input', function () {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(filterItems, 500);
});

document.getElementById('filter-model').addEventListener('change', function () {
    filterItems();
});


function searchByModel(actorName) {
    document.getElementById('filter-model').value = actorName;
    filterItems();
}