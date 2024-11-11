let map;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        center: { lat: 35.9447, lng: 126.6835 },
        zoom: 17,
    });
}

initMap();