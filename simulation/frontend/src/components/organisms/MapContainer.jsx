import { MapContainer as LeafletMap, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { esiToColor } from '../../utils/esiColor';
import MapLegend from '../molecules/MapLegend';

export default function MapContainer({ neighborhoods, center, onNeighborhoodClick }) {
  const defaultCenter = center ?? [32.22, -110.97];

  function styleFeature(feature) {
    const score = feature.properties?.esi_score ?? 0;
    return {
      fillColor: esiToColor(score),
      fillOpacity: 0.6,
      color: '#ffffff',
      weight: 1,
    };
  }

  function onEachFeature(feature, layer) {
    layer.on('click', () => onNeighborhoodClick(feature.properties));
  }

  const geojsonData = {
    type: 'FeatureCollection',
    features: (neighborhoods ?? []).map(n => ({
      type: 'Feature',
      properties: n,
      geometry: n.geojson,
    })),
  };

  return (
    <div className="relative h-full w-full">
      <LeafletMap
        center={defaultCenter}
        zoom={12}
        className="h-full w-full"
        key={JSON.stringify(defaultCenter)}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />
        {neighborhoods?.length > 0 && (
          <GeoJSON data={geojsonData} style={styleFeature} onEachFeature={onEachFeature} />
        )}
      </LeafletMap>
      <div className="absolute bottom-4 left-4 z-[1000]">
        <MapLegend />
      </div>
    </div>
  );
}
