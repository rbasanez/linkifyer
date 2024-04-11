var libraryData;
var filteredData;
var itemsPerPage = 12;
var currentPage = 1;

var filterData = (filter) => {
    return libraryData.filter(function (item) {
        return !filter || (item.keys && item.keys.includes(filter));
    });
};

var getTotalPages = () => {
    return Math.ceil(filteredData.length / itemsPerPage);
};

async function loadData(url) {
    const response = await fetch(url);
    libraryData = await response.json();
    filteredData = libraryData;
    let totalPages = getTotalPages();
    displayItems(1);
    createPaginationButtons(1, totalPages);
}

document.getElementById('filter-form').addEventListener('submit', function (event) {
    event.preventDefault();
    var filterInput = document.getElementById('filter-input').value.trim().toLowerCase();
    filteredData = filterData(filterInput);
    var totalPages = getTotalPages();
    displayItems(1);
    createPaginationButtons(1, totalPages);
});

function updatePagination(pageNumber) {
    currentPage = pageNumber;
    displayItems(currentPage);
    createPaginationButtons(currentPage, getTotalPages());
}

function createPaginationButtons(activePage, totalPages) {
    var paginationContainer1 = document.getElementById('pagination-1');
    var paginationContainer2 = document.getElementById('pagination-2');
    paginationContainer1.innerHTML = '';
    if (totalPages > 1) {
        var startPage = 1;
        var endPage = totalPages;
        if (totalPages > 3) {
            if (activePage <= 2) {
                endPage = 3;
            } else if (activePage >= totalPages - 1) {
                startPage = totalPages - 2;
            } else {
                startPage = activePage - 1;
                endPage = activePage + 1;
            }
            if (startPage > 1) {
                paginationContainer1.appendChild(createPageButton(1));
                if (startPage > 2) paginationContainer1.appendChild(createEllipsis());
            }
            for (var p = startPage; p <= endPage; p++) {
                paginationContainer1.appendChild(createPageButton(p));
            }
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) paginationContainer1.appendChild(createEllipsis());
                paginationContainer1.appendChild(createPageButton(totalPages));
            }
        } else {
            for (var p = 1; p <= totalPages; p++) {
                paginationContainer1.appendChild(createPageButton(p));
            }
        }
    }
    paginationContainer2.innerHTML = paginationContainer1.innerHTML;
}

function createPageButton(pageNumber) {
    var button = document.createElement('button');
    if (pageNumber === currentPage) {
        button.setAttribute('class', 'btn btn-sm btn-secondary text-white page-button');
        button.setAttribute('disabled', true);
    } else {
        button.setAttribute('class', 'btn btn-sm btn-info text-white page-button');
    }
    button.setAttribute('onclick', `updatePagination(${pageNumber})`)
    button.textContent = pageNumber;
    return button;
}

function createEllipsis() {
    var button = document.createElement('button');
    button.setAttribute('class', 'btn btn-sm btn-light btn-secondary text-dark page-button');
    button.setAttribute('disabled', true);
    button.textContent = '...';
    return button;
}

function displayItems(pageNumber) {
    var itemsContainer = document.getElementById('library');
    itemsContainer.innerHTML = ''; // Clear existing items
    if (!filteredData) {
        console.error("Filtered data is not available.");
        return;
    }
    var startIndex = (pageNumber - 1) * itemsPerPage; // Assuming 12 items per page
    var endIndex = Math.min(startIndex + itemsPerPage, filteredData.length);
    var itemsToDisplay = filteredData.slice(startIndex, endIndex);
    itemsToDisplay.forEach(function (item) {
        var itemTitle = item.title ? item.title : '';
        var itemTags = item.tags ? item.tags : '';
        var itemDescription = item.description ? item.description : '';
        var itemPoster = static + (item.poster ? item.poster : 'img/img_404.jpg');
        var itemIcon = static + (item.icon ? item.icon : 'img/icon_404.png');
        var itemSearch = itemTitle.replace("'", "");

        var div = document.createElement('div');
        div.setAttribute('class', 'col py-2 d-flex text-center justify-content-center');
        div.setAttribute('tags', (itemTags + itemTitle).toLowerCase() + itemDescription.toLowerCase());
        div.innerHTML = `
            <div class="card border-0 w-100">
                <a class="ratio ratio-16x9 cover position-relative" href="${item.url}" target="_blank" style="background-image:url('${itemPoster}');">
                    ${item.favorite == 1 ? `<a class="btn btn-warning position-absolute top-0 end-0 m-2 p-1" onclick="actionFavorite(this, ${item.item_id})"><i class="bi bi-bookmark-fill"></i></a>` : `<a class="btn btn-light position-absolute top-0 end-0 m-2 p-1" onclick="actionFavorite(this, ${item.item_id})"><i class="bi bi-bookmark"></i></a>`}
                </a>
                <div class="card-body h-100">
                    <p class="card-title"><img src="${itemIcon}" width="16"></p>
                    <p class="card-text text-secondary lh-sm">${itemTitle}</p>
                </div>
                <div class="card-body p-0 pb-2">
                    <button class="btn btn-light" onclick="actionSearchWeb('${itemSearch}')"><p><img src="static/img/duckduckgo.svg" width="16"> Search more</p></button>
                </div>
                <div class="card-body p-0">
                    <div class="btn-group mr-2 w-100 " role="group">
                        <button class="btn btn-info text-white py-3" onclick="actionDelete('${item.user_id}', '${item.item_hash}')" data-bs-toggle="tooltip" data-bs-title="Delete"><i class="bi bi-trash"></i></button>
                        <button class="btn btn-info text-white py-3" onclick="actionEdit('${item.url}')" data-bs-toggle="tooltip" data-bs-title="Edit"><i class="bi bi-pencil-square"></i></button>
                        <button class="btn btn-info text-white py-3" onclick="actionGoTo('${item.url}')" data-bs-toggle="tooltip" data-bs-title="Go To"><i class="bi bi-play-fill"></i></button>
                    </div>
                </div>
            </div>
        `;
        itemsContainer.appendChild(div);
    });
}

function actionFavorite(element, id, hash) {
    fetch(`{{url_for("favorite")}}?item_id=${id}`, { method: 'GET' })
        .then(response => {
            if (!response.ok) { sendAlert(`Network response: ${response.text()}`, 'danger'); return null; }
            else { return response.text(); }
        })
        .then(data => {
            if (data == "1") {
                let icon = element.querySelector('i');
                if (element.classList.contains('btn-light')) {
                    element.classList.remove('btn-light');
                    element.classList.add('btn-warning');
                    icon.classList.remove('bi-bookmark');
                    icon.classList.add('bi-bookmark-fill');
                } else {
                    element.classList.remove('btn-warning');
                    element.classList.add('btn-light');
                    icon.classList.remove('bi-bookmark-fill');
                    icon.classList.add('bi-bookmark');
                }
            }
        });
}