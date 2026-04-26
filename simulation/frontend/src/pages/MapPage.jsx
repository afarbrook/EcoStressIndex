import { useState, useEfect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../utils/supabase';
import { fetchCity, fetchNeighborhood, fetchSimulation, logSearch } from '../utils/api';
import Navbar from '../components/organisms/Navbar';
import Sidebar from '../components/organisms/Sidebar';
import MapContainer from '../components/organisms/MapContainer';
import NeighborhoodPanel from '../components/organisms/NeighborhoodPanel';

export default function MapPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [city, setCity] = useState(null);
  const [cityCenter, setCityCenter] = useState(null);
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [weights, setWeights] = useState(null);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isPanelLoading, setIsPanelLoading] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
  }, []);

  async function handleSearch(query) {
    setIsSearching(true);
    try {
      const data = await fetchCity(query);
      setCity(data.city);
      setCityCenter([data.city_center.lat, data.city_center.lon]);
      setNeighborhoods(data.neighborhoods);
      setWeights(data.weights);
      setSelectedNeighborhood(null);
      setSimulation(null);
      logSearch(query, data.city);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  }

  async function handleNeighborhoodClick(properties) {
    setSelectedNeighborhood(properties);
    setSimulation(null);
    setIsPanelLoading(true);
    try {
      const [detail, sim] = await Promise.all([
        fetchNeighborhood(city, properties.name),
        fetchSimulation(city, properties.name),
      ]);
      setSelectedNeighborhood(detail);
      setSimulation(sim);
    } catch (e) {
      console.error(e);
    } finally {
      setIsPanelLoading(false);
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    localStorage.removeItem('esi_token');
    navigate('/login');
  }

  return (
    <div className="flex flex-col h-screen">
      <Navbar city={city} user={user} onLogout={handleLogout} />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-56 border-r border-gray-200 shrink-0">
          <Sidebar weights={weights} onSearch={handleSearch} isLoading={isSearching} onLogout={handleLogout} />
        </div>
        <div className="flex-1">
          <MapContainer
            neighborhoods={neighborhoods}
            center={cityCenter}
            onNeighborhoodClick={handleNeighborhoodClick}
          />
        </div>
        <div className="w-72 border-l border-gray-200 shrink-0">
          <NeighborhoodPanel
            neighborhood={selectedNeighborhood}
            simulation={simulation}
            isLoading={isPanelLoading}
          />
        </div>
      </div>
    </div>
  );
}
