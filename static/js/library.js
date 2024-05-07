var libraryData;
var filteredData;
var itemsPerPage = 12;
var currentPage = 1;
var paginationSize = 4


async function loadData(url) {
    const response = await fetch(url);
    libraryData = await response.json();
    filteredData = libraryData;
    let totalPages = getTotalPages();
    displayItems(currentPage);
    createPaginationButtons(1, totalPages);
}

var filterLibraryData = (filter) => {
    return libraryData.filter(function (item) {
        return !filter || (item.keys && item.keys.includes(filter));
    });
};

function filterData(){
    var filterInput = document.getElementById('filter-input').value.trim().toLowerCase();
    filteredData = filterLibraryData(filterInput);
    var totalPages = getTotalPages();
    displayItems(currentPage);
    createPaginationButtons(1, totalPages);
}

document.getElementById('filter-form').addEventListener('submit', function (event) {
    event.preventDefault();
    filterData();
});


var getTotalPages = () => {
    return Math.ceil(filteredData.length / itemsPerPage);
};


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
        if (totalPages > paginationSize) {
            if (activePage <= 2) {
                endPage = paginationSize;
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
        button.setAttribute('class', 'btn btn-secondary text-white');
        button.setAttribute('disabled', true);
    } else {
        button.setAttribute('class', 'btn btn-info text-white');
    }
    button.setAttribute('onclick', `updatePagination(${pageNumber})`)
    button.textContent = pageNumber;
    return button;
}

function createEllipsis() {
    var button = document.createElement('button');
    button.setAttribute('class', 'btn btn-light btn-secondary text-dark');
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
        div.setAttribute('class', 'col d-flex mb-4 text-center justify-content-center');
        div.setAttribute('tags', (itemTags + itemTitle).toLowerCase() + itemDescription.toLowerCase());
        div.innerHTML = `
            <div class="card border-0 w-100">
                <a class="ratio ratio-16x9 cover position-relative rounded-top" href="${item.url}" target="_blank" style="background-image:url('${itemPoster}');" data-bs-toggle="tooltip-lib" data-bs-placement="bottom" data-bs-title="Go to URL">
                    <a class="btn position-absolute top-0 end-0 m-2 p-1" onclick="actionFavorite(this, ${item.item_id})"><i class="${item.favorite == 1 ? `bi bi-bookmark-fill` : `bi bi-bookmark` }"></i></a>
                </a>
                <div class="card-body h-100">
                    <p class="card-title"><img src="${itemIcon}" width="16"></p>
                    <p class="card-text text-capitalize text-secondary lh-sm" data-bs-toggle="tooltip-lib" data-bs-title="${itemTitle.toLowerCase()}">${getTrimmedText(itemTitle, 50).toLowerCase()}</p>
                </div>
                <!-- <div class="card-body p-0 pb-2">
                    <button class="btn btn-light" onclick="actionSearchWeb('${itemSearch}')"><p><img src="static/img/duckduckgo.svg" width="16"> Search more</p></button>
                </div> -->
                <div class="card-body p-0">
                    <div class="btn-group mr-2 w-100 " role="group">
                        <button class="btn btn-info text-white py-3" onclick="actionDelete('${item.item_id}')" data-bs-toggle="tooltip-lib" data-bs-title="Delete"><i class="bi bi-trash"></i></button>
                        <button class="btn btn-info text-white py-3" onclick="actionEdit('${item.url}')" data-bs-toggle="tooltip-lib" data-bs-title="Edit"><i class="bi bi-pencil-square"></i></button>
                        <button class="btn btn-info text-white py-3" onclick="actionGoTo('${item.url}')" data-bs-toggle="tooltip-lib" data-bs-title="Go to URL"><i class="bi bi-play-fill"></i></button>
                    </div>
                </div>
            </div>
        `;
        itemsContainer.appendChild(div);
    });
    const tooltipLibTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip-lib"]')
    const tooltipLibList = [...tooltipLibTriggerList].map(element => new bootstrap.Tooltip(element))
}



const getTrimmedText = (text, max_lenght) => {
    if (text.length > max_lenght) {
        return text.substring(0, max_lenght).trimEnd() + '...';
    } else {
        return text;
    }
};