document.addEventListener('DOMContentLoaded', function () {
    flatpickr('#check-in', {
        dateFormat: 'Y-m-d',
        minDate: 'today',
        defaultDate: 'today',
    });


    flatpickr('#check-out', {
        dateFormat: 'Y-m-d',
        minDate: 'today',
        defaultDate: new Date().fp_incr(1),
    });
    document.getElementById('guests').value = 1;
});

function checkAvailability() {
    var checkInDate = document.getElementById('check-in').value;
    var checkOutDate = document.getElementById('check-out').value;
    var adults = document.getElementById('adults').value;
    var children = document.getElementById('children').value;

    console.log('Pobyt od:', checkInDate);
    console.log('Pobyt do:', checkOutDate);
    console.log('Liczba dorosłych:', adults);
    console.log('Liczba dzieci:', children);
}
