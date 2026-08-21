// MapView.jsx — Interactive Leaflet map with color-coded station markers

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon path issues with Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const STRESS_COLORS = {
  safe:            '#22c55e',
  'semi-critical': '#f59e0b',
  critical:        '#f97316',
  'over-exploited':'#ef4444',
  unknown:         '#64748b',
};

const AQUIFER_SHAPES = {
  alluvial:   'circle',
  'hard-rock':'square',
  coastal:    'diamond',
};

function createMarkerIcon(stress, aquifer, isSelected) {
  const color = STRESS_COLORS[stress] || STRESS_COLORS.unknown;
  const size = isSelected ? 20 : 14;
  const borderSize = isSelected ? 3 : 2;
  const shape = AQUIFER_SHAPES[aquifer] || 'circle';

  let borderRadius;
  let clipPath;
  if (shape === 'square') {
    borderRadius = '3px';
    clipPath = 'none';
  } else if (shape === 'diamond') {
    borderRadius = '2px';
    clipPath = 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)';
  } else {
    borderRadius = '50%';
    clipPath = 'none';
  }

  const glowSize = isSelected ? 14 : 8;
  const html = `
    <div style="
      position: relative;
      width: ${size}px;
      height: ${size}px;
    ">
      <div style="
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: ${size + glowSize}px;
        height: ${size + glowSize}px;
        border-radius: 50%;
        background: ${color};
        opacity: 0.2;
        animation: ${isSelected ? 'markerPulse 1.5s ease-out infinite' : 'markerPulse 2.5s ease-out infinite'};
      "></div>
      <div style="
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        border-radius: ${borderRadius};
        clip-path: ${clipPath};
        border: ${borderSize}px solid rgba(255,255,255,0.8);
        box-shadow: 0 0 ${isSelected ? 12 : 6}px ${color};
        cursor: pointer;
      "></div>
    </div>
  `;

  return L.divIcon({
    html,
    className: '',
    iconSize: [size + glowSize, size + glowSize],
    iconAnchor: [(size + glowSize) / 2, (size + glowSize) / 2],
    popupAnchor: [0, -(size + glowSize) / 2],
  });
}

export default function MapView({ stations, selectedId, onSelectStation }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef({});

  // Initialize map
  useEffect(() => {
    if (mapInstanceRef.current) return;

    const map = L.map(mapRef.current, {
      center: [22.5, 78.9],
      zoom: 5,
      zoomControl: false,
      attributionControl: true,
    });

    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '© OpenStreetMap contributors © CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
      }
    ).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    mapInstanceRef.current = map;
  }, []);

  // Update markers when stations change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !stations?.length) return;

    // Remove old markers
    Object.values(markersRef.current).forEach(m => m.remove());
    markersRef.current = {};

    stations.forEach(s => {
      const isSelected = s.station_id === selectedId;
      const icon = createMarkerIcon(s.stress_level, s.aquifer_type, isSelected);

      const popupContent = `
        <div style="min-width:200px; font-family: Inter, sans-serif;">
          <div style="font-weight:700; font-size:13px; margin-bottom:4px; color:#f0f9ff">
            ${s.station_name}
          </div>
          <div style="font-size:11px; color:#94a3b8; margin-bottom:8px">
            ${s.district}, ${s.state}
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
            <span style="color:#94a3b8">Current Level</span>
            <span style="color:#00d4ff; font-weight:600">${s.latest_level != null ? s.latest_level.toFixed(1) + ' m bgl' : '—'}</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
            <span style="color:#94a3b8">Aquifer Type</span>
            <span style="color:#f0f9ff; font-weight:500; text-transform:capitalize">${s.aquifer_type}</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:#94a3b8">Status</span>
            <span style="font-weight:700; text-transform:capitalize; color:${STRESS_COLORS[s.stress_level] || '#64748b'}">${s.stress_level || 'Unknown'}</span>
          </div>
        </div>
      `;

      const marker = L.marker([s.latitude, s.longitude], { icon })
        .bindPopup(popupContent, { maxWidth: 240 })
        .addTo(map);

      marker.on('click', () => {
        onSelectStation(s.station_id);
      });

      markersRef.current[s.station_id] = marker;
    });
  }, [stations, selectedId]);

  // Pan to selected station
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !selectedId || !stations?.length) return;

    const s = stations.find(st => st.station_id === selectedId);
    if (s) {
      map.setView([s.latitude, s.longitude], Math.max(map.getZoom(), 7), {
        animate: true, duration: 0.8
      });
    }
  }, [selectedId]);

  return (
    <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
  );
}
