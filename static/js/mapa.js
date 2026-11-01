// Mapas con Leaflet: el mapa de todos los reportes, el punto de un reporte
// y el selector del formulario para marcar dónde está el problema.
(() => {
  const COLORES = { pendiente: '#a86b00', proceso: '#1d5fa8', resuelto: '#2f7d4f', rechazado: '#b3261e' };
  const ZOOM_CERCA = 17;

  const leerJSON = (id) => JSON.parse(document.getElementById(id).textContent);

  const escapar = (texto) => {
    const caja = document.createElement('div');
    caja.textContent = texto;
    return caja.innerHTML;
  };

  const crearMapa = (elemento, centro, zoom) => {
    const mapa = L.map(elemento).setView(centro, zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);
    return mapa;
  };

  const marcaDeEstado = (punto, clase) => L.circleMarker(punto, {
    radius: 10, color: '#ffffff', weight: 2, fillColor: COLORES[clase] || COLORES.pendiente, fillOpacity: 0.9,
  });

  // 1) Mapa con todos los reportes que tienen coordenadas.
  const contenedor = document.getElementById('mapa-reportes');
  if (contenedor) {
    const config = leerJSON('mapa-config');
    const mapa = crearMapa(contenedor, config.centro, config.zoom);
    const marcas = leerJSON('mapa-puntos').map((p) => marcaDeEstado([p.lat, p.lng], p.clase)
      .bindPopup(`<strong>${escapar(p.titulo)}</strong><br>${escapar(p.estado)} · ${escapar(p.categoria)}`
        + `<br><a href="${p.url}">Ver reporte</a>`)
      .addTo(mapa));
    if (marcas.length) {
      mapa.fitBounds(L.featureGroup(marcas).getBounds(), { padding: [40, 40], maxZoom: ZOOM_CERCA });
    }
  }

  // 2) El punto de un solo reporte, en su página de detalle.
  document.querySelectorAll('[data-mapa-punto]').forEach((elemento) => {
    const punto = [parseFloat(elemento.dataset.lat), parseFloat(elemento.dataset.lng)];
    marcaDeEstado(punto, elemento.dataset.clase).addTo(crearMapa(elemento, punto, ZOOM_CERCA));
  });

  // 3) Selector del formulario: tocar el mapa llena la latitud y la longitud.
  const selector = document.getElementById('mapa-elegir');
  if (selector) {
    const config = leerJSON('mapa-config');
    const latitud = document.getElementById('id_latitud');
    const longitud = document.getElementById('id_longitud');
    const aviso = document.getElementById('mapa-aviso');
    const hayPunto = () => latitud.value !== '' && longitud.value !== '';
    const puntoActual = () => L.latLng(parseFloat(latitud.value), parseFloat(longitud.value));

    const mapa = hayPunto() ? crearMapa(selector, puntoActual(), ZOOM_CERCA) : crearMapa(selector, config.centro, config.zoom);
    let marca = null;

    const poner = (punto, acercar = false) => {
      punto = punto.wrap();
      if (marca) {
        marca.setLatLng(punto);
      } else {
        marca = L.marker(punto, { draggable: true }).addTo(mapa);
        marca.on('dragend', () => poner(marca.getLatLng()));
      }
      latitud.value = punto.lat.toFixed(6);
      longitud.value = punto.lng.toFixed(6);
      aviso.textContent = '';
      if (acercar) mapa.setView(punto, ZOOM_CERCA);
    };

    if (hayPunto()) poner(puntoActual());
    mapa.on('click', (evento) => poner(evento.latlng));
    [latitud, longitud].forEach((campo) => campo.addEventListener('change', () => {
      if (hayPunto()) poner(puntoActual(), true);
    }));

    document.getElementById('mapa-mi-ubicacion').addEventListener('click', () => {
      if (!navigator.geolocation) {
        aviso.textContent = 'Tu navegador no permite obtener la ubicación. Marca el lugar tocando el mapa.';
        return;
      }
      aviso.textContent = 'Buscando tu ubicación…';
      navigator.geolocation.getCurrentPosition(
        (posicion) => poner(L.latLng(posicion.coords.latitude, posicion.coords.longitude), true),
        () => { aviso.textContent = 'No se pudo obtener tu ubicación. Marca el lugar tocando el mapa.'; },
        { enableHighAccuracy: true, timeout: 10000 },
      );
    });

    document.getElementById('mapa-quitar').addEventListener('click', () => {
      if (marca) {
        mapa.removeLayer(marca);
        marca = null;
      }
      latitud.value = '';
      longitud.value = '';
    });
  }
})();
