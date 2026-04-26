import Navbar from './components/organisms/Navbar'
import Sidebar from './components/organisms/Sidebar'
import NeighborhoodPanel from './components/organisms/NeighborhoodPanel'
import MapContainer from './components/organisms/MapContainer'
import LoginCard from './components/organisms/LoginCard'
import { mockNeighborhood, mockWeights, mockSimulation } from './utils/mockData'

function App() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar city="Tucson, AZ" user={{ email: 'demo@esi.com' }} onLogout={() => {}} />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-56 border-r border-gray-200">
          <Sidebar
            weights={mockWeights}
            onSearch={(q) => console.log(q)}
            isLoading={false}
            onLogout={() => {}}
          />
        </div>
        <div className="flex-1">
          <MapContainer
            neighborhoods={[]}
            center={[32.22, -110.97]}
            onNeighborhoodClick={(n) => console.log(n)}
          />
        </div>
        <div className="w-72 border-l border-gray-200">
          <NeighborhoodPanel
            neighborhood={mockNeighborhood}
            simulation={mockSimulation}
            isLoading={false}
          />
        </div>
      </div>
    </div>
  )
}

export default App
