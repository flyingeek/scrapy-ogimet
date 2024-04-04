function throttle(func, wait, leading, trailing, context) {
    let ctx, args, result;
    let timeout = null;
    let previous = 0;
    const later = function() {
        previous = new Date;
        timeout = null;
        result = func.apply(ctx, args);
    };
    return function() {
        var now = new Date;
        if (!previous && !leading) previous = now;
        var remaining = wait - (now - previous);
        ctx = context || this;
        args = arguments;
        // Si la période d'attente est écoulée
        if (remaining <= 0) {
            // Réinitialiser les compteurs
            clearTimeout(timeout);
            timeout = null;
            // Enregistrer le moment du dernier appel
            previous = now;
            // Appeler la fonction
            result = func.apply(ctx, args);
        } else if (!timeout && trailing) {
            // Sinon on s’endort pendant le temps restant
            timeout = setTimeout(later, remaining);
        }
        return result;
    };
}
async function readJsonWithProgress(response, offset=0) {
  const reader = response.body.getReader();
  const contentLength = +response.headers.get('Content-Length');

  let receivedLength = 0;
  let chunks = [];
  const progressElement = document.querySelector('progress');
  // Shows progress if it takes more than 500ms
  setTimeout(() => {
    if (parseFloat(progressElement.value) <95) {
      document.querySelector('.progress').classList.remove("d-none");
    }
  }, 500);
  while(true) {
    const {done, value} = await reader.read();
    if (done) {
      break;
    }
    chunks.push(value);
    receivedLength += value.length;
    //We have 2 downloads to perform, each represent 50%
    progressElement.value = offset + (50 * receivedLength/contentLength);
  }
  let chunksAll = new Uint8Array(receivedLength); // (4.1)
  let position = 0;
  for(let chunk of chunks) {
    chunksAll.set(chunk, position); // (4.2)
    position += chunk.length;
  }
  const result = new TextDecoder("utf-8").decode(chunksAll);
  return JSON.parse(result);
};

const data = {};
const hash = window.location.hash;

const getAttribution = (source) => (source === 'oscar')
    ? `${data['oscar'].features.length} WMO from <a href="https://oscar.wmo.int" target="_blank">oscar.wmo.int</a>`
    : `${data['ogimet'].features.length} WMO from <a href="https://www.ogimet.com" target="_blank">ogimet.com</a>`;
const map = new maplibregl.Map({
    container: 'map',
    style: 'https://flyingeek.github.io/scrapy-ogimet/mapstyle.json', // style URL
    center: [0, 0], // starting position [lng, lat]
    zoom: 0.5, // starting zoom
    renderWorldCopies: false,
    // attributionControl: false
});
document.getElementById('source').addEventListener('change', e => {
    const [source, cluster] = e.target.value.split("_");
    if (source === 'ogimet') {
        document.getElementById('filter_ogimet').classList.remove("d-none");
        document.getElementById('filter_oscar').classList.add("d-none");
    } else {
        document.getElementById('filter_oscar').classList.remove("d-none");
        document.getElementById('filter_ogimet').classList.add("d-none");
    }
    const changeEvent = new Event('change');
    document.getElementById((source === 'ogimet') ? 'filter_ogimet' : 'filter_oscar').dispatchEvent(changeEvent);
    const wmoSource = map.getSource('wmo');
    wmoSource.workerOptions.cluster = !!cluster;
    wmoSource.setData(data[source]);
    wmoSource.attribution = getAttribution(source);
});
document.getElementById('filter_oscar').addEventListener('change', e => {
    const selectValue = e.target.value;
    let filter = null;
    if (selectValue === 'non-operational') {
        filter = ['!=', ["get", "operational"], 'operational'];
    }else if (selectValue === 'operational') {
        filter = ['==', ["get", "operational"], 'operational'];
    }else if (selectValue === 'closed') {
        filter = ['==', ["get", "operational"], 'closed'];
    }else if (selectValue === 'legacy') {
        filter = ["any", ['!=', ["get", "wid"], null], ['!=', ["get", "wid_guess"], null]];
    }
    map.setFilter('unclustered-stations', filter);
});
document.getElementById('filter_ogimet').addEventListener('change', e => {
    const selectValue = e.target.value;
    let filter = null;
    if (selectValue === 'closed') {
        filter = ['==', ["get", "closed"], true];
    }else if (selectValue === 'open') {
        filter = ['==', ["get", "closed"], false];
    }else if (selectValue === 'no-wigos') {
        filter = ['==', ["get", "wigos"], null];
    }else if (selectValue === 'wigos') {
        filter = ['!=', ["get", "wigos"], null];
    }
    map.setFilter('unclustered-stations', filter);
});
map.on('load', async () => {
    const initialSource = document.getElementById('source').value;
    const route = (hash.indexOf('_') > 0) ? hash.slice(1) : '';
    data['ogimet'] = await fetch('./data/ogimet/ogimet.geojson').then(readJsonWithProgress);
    const findWMO = (widOrIcao) => data['ogimet'].features.find(o => o.properties.wid === widOrIcao || o.properties.icao === widOrIcao);
    let routeCoordinates = [];
    //Transform list of WMO indexes to a list of coordinates
    for (widOrIcao of route.split('_').filter(w => w !== '')) {
        wmo = findWMO(widOrIcao);
        if (!wmo) { // not valid input => abort
            routeCoordinates = [];
            break;
        }
        // adjust coordinates to allow maplibre to cross antemeridian
        const startLng = routeCoordinates.length > 0 ? routeCoordinates[routeCoordinates.length-1][0] : null;
        const endLng = wmo.geometry.coordinates[0];
        if (startLng && Math.abs((endLng - startLng)) > 180) {
            if (endLng - startLng >= 180) {
                endLng -= 360;
            } else if (endLng - startLng < 180) {
                endLng += 360;
            }
        }
        routeCoordinates.push([endLng, wmo.geometry.coordinates[1]]);
    }
    map.addSource('route', {
        type: 'geojson',
        data: {
            type: "FeatureCollection",
            features: [
                {
                    type: 'Feature',
                    geometry: {
                        type: 'LineString',
                        coordinates: routeCoordinates
                    }
                }
            ]
        }
    });
    map.addSource('wmo', {
        type: 'geojson',
        data: data[initialSource],
        cluster: false,
        clusterMaxZoom: 3, // Max zoom to cluster points on
        clusterRadius: 50, // Radius of each cluster when clustering points (defaults to 50)
        attribution: getAttribution(initialSource)
    });

    map.addLayer({
        id: 'unclustered-stations',
        type: 'symbol',
        source: 'wmo',
        layout: {
            'icon-allow-overlap': false,
            'icon-ignore-placement': false,
            'icon-image': [
                'case',
                ['==', ["get", "closed"], true], "maki:cross",
                ['==', ["get", "operational"], 'closed'], "maki:cross",
                ['all', ['has', 'operational'],['!=', ["get", "operational"], 'operational']], "maki:caution",
                ["all", ['has', 'icao'], ['!=', ["get", "icao"], null]], "maki:airfield"
                ,'custom:circle'
            ],
            'icon-size': [
                "interpolate", ["linear"], ["zoom"],
                // zoom is 1 (or less
                1, 0.8,
                // zoom is 10 (or greater)
                6, 1.5
            ],
        },
        paint: {
            'icon-color': ["case",
                ["all", ["==", ['get', 'wid'], null], ['has', 'wid_guess'], ["!=", ['get', 'wid_guess'], null]], '#008B8B',
                "#6a5acd"
            ],
              'icon-halo-color': [
                'case',
                ["all", ["==", ['get', 'wid'], null], ["==", ['get', 'wid_guess'], null]], '#ffa323',
                ["==",['get', 'wigos'], null], '#f00',
                "#fff"
            ],
            'icon-halo-width': 1,
        }
    });

    map.addLayer({
        id: 'route-layer',
        type: 'line',
        source: 'route',
        visible: routeCoordinates.length > 1,
        layout: {
            'line-cap': 'round',
            'line-join': 'round'
        },
        paint: {
            'line-color': '#ed6498',
            'line-width': 5,
            'line-opacity': 0.8
        }
    });
    // Create a popup, but don't add it to the map yet.
    const popup = new maplibregl.Popup({
        closeButton: true,
        closeOnClick: false
    });
    const showPopup = e => {
        const coordinates = e.features[0].geometry.coordinates.slice();
        const properties = e.features[0].properties;

        // Ensure that if the map is zoomed out such that
        // multiple copies of the feature are visible, the
        // popup appears over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        const descriptionLines = [];
        if (properties["name"]) {
            descriptionLines.push(`<p class="name">${properties["name"]}</p>`);
        }
        descriptionLines.push('<dl>');
        const parts = [];
        if (properties['icao']) parts.push(properties['icao']);
        if (properties['wid'] || properties['wid_guess']) {
            parts.push(`<a href="https://www.ogimet.com/cgi-bin/gsynres?ord=REV&ndays=7&ind=${properties['wid'] || properties['wid_guess'] }" target="_blank">${properties['wid'] || properties['wid_guess']}</a>`);
        } else {
            parts.push(`missing`);
        }
        descriptionLines.push(
            `<dt class="wmo${(properties['wid_guess']) ? ' guess' : ''}">wmo</dt>` +
            `<dd> ${parts.join('&nbsp;/&nbsp;')}</dd>`
        );
        if (properties["country"]) {
            descriptionLines.push(`<dt class="country">country</dt><dd>${properties["country"]}</dd>`);
        }
        if (properties["wigosStationIdentifiers"]) {
            const links = (properties["wigosStationIdentifiers"]).split(';').map(wigosId => `<a href="https://oscar.wmo.int/surface/index.html#/search/station/stationReportDetails/${wigosId}" target="_blank">${wigosId}</a>`);
            descriptionLines.push(`<dt class="oscar">oscar</dt><dd>${links.join('<br>')}</dd>`);
        }else if (properties["wigos"]) {
            descriptionLines.push(`<dt class="oscar">oscar</dt><dd><a href="https://oscar.wmo.int/surface/index.html#/search/station/stationReportDetails/${properties['wigos']}" target="_blank">${properties['wigos']}</a></dd>`);
        }else if (properties["wid"]) {
            descriptionLines.push(`<dt class="oscar missing">oscar</dt><dd><a href="https://oscar.wmo.int/surface/index.html#/search/station/stationReportDetails/0-20000-0-${properties['wid']}" target="_blank">missing</a></dd>`);
        }else{
            descriptionLines.push(`<dt class="oscar missing">oscar</dt><dd>missing</dd>`)
        }
        if (properties["closed"]){
            descriptionLines.push(`<dt class="status">status</dt><dd>closed</dd`)
        }
        if (properties["operational"]){
            descriptionLines.push(`<dt class="status">status</dt><dd>${properties["operational"]}</dd>`)
        }
        descriptionLines.push('</dl>')
        popup.setLngLat(coordinates).setHTML(`<div class="wmo-popup">${descriptionLines.join('')}</div>`).addTo(map);
    }
    const cursorPointerAndShowPopup = e => {
        map.getCanvas().style.cursor = 'pointer';
        showPopup(e);
    };
    const cursorDefault = () => map.getCanvas().style.cursor = '';

    map.on('click', 'unclustered-stations', showPopup);

    map.on('mouseover', 'unclustered-stations', cursorPointerAndShowPopup);

    map.on('mouseleave', 'unclustered-stations', cursorDefault);

    map.on('zoom', throttle((e) => {
      const map = e.target;
      const zoom = map.getZoom();
      map.setLayoutProperty('unclustered-stations', 'icon-allow-overlap', zoom >= 5);
      document.getElementById('zoom-level').innerText = zoom.toFixed(1);
    }, 100));
    document.getElementById('zoom-level').innerText = map.getZoom().toFixed(1);

    data['oscar'] = await fetch('./data/oscar/oscar.geojson').then(response => readJsonWithProgress(response, 50));
    document.querySelector("#map fieldset").classList.remove("d-none");
    document.querySelector('.progress').classList.add("d-none");
});
