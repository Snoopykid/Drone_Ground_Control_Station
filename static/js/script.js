let map;
let droneMarker = null;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        center: { lat: 35.9447, lng: 126.6835 },
        zoom: 17,
    });
}

// 드론 위치 마커 업데이트 (index.html의 SocketIO에서 호출)
function updateMapMarker(lat, lng) {
    if (!map) return;
    const position = { lat: lat, lng: lng };
    if (droneMarker) {
        droneMarker.setPosition(position);
    } else {
        droneMarker = new google.maps.Marker({
            position: position,
            map: map,
            title: '드론 현재 위치',
        });
    }
    map.panTo(position);
}

// initMap()은 index.html의 DOMContentLoaded에서 호출하므로 여기서는 제거
