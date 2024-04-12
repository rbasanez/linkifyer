var currentColsLG = 4; // Initial value of N
var minColsLG = 1; // Minimum value of N
var maxColsLG = 6; // Maximum value of N

function updateRowColsLG(n) {
    var element = document.getElementById('library');
    element.className = element.className.replace(/row-cols-lg-\d+/, '');
    element.classList.add('row-cols-lg-' + n);
    currentColsLG = n;
}

function decrementColsLG() {
    if (currentColsLG > minColsLG) {
        updateRowColsLG(currentColsLG - 1);
    }
}

function incrementColsLG() {
    if (currentColsLG < maxColsLG) {
        updateRowColsLG(currentColsLG + 1);
    }
}