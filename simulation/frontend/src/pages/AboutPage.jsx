import { useNavigate } from 'react-router-dom';
import Button from '../components/atoms/Button';

const team = [
  {
    name: 'Christopher Gonzalez',
    avatar: null,
    contributions: [
      'Frontend architecture & design system',
      'Landing page & UI animations',
      'Simulation layer & map interface',
      'React component library',
    ],
    email: 'chris.gonzalez9388@gmail.com',
    linkedin: 'https://www.linkedin.com/in/christopher-gonzalez-ua/',
    github: 'https://github.com/slumppd',
  },
  {
    name: 'Alex Farbrook',
    avatar: null,
    contributions: [
      'Flask backend & API design',
      'ESI score computation engine',
      'Data source integrations',
      'Repository setup & architecture',
    ],
    email: 'afarbrook@gmail.com',
    linkedin: 'https://www.linkedin.com/in/alexfarbrook/',
    github: 'https://github.com/afarbrook',
  },
];

function Avatar({ name }) {
  const initials = name.split(' ').map(n => n[0]).join('');
  return (
    <div className="w-24 h-24 rounded-full bg-brand-light flex items-center justify-center shrink-0">
      <span className="text-2xl font-medium text-brand-dark">{initials}</span>
    </div>
  );
}

function ContactLink(props) {
  return (
   <a>    
      href={props.href}
      target="_blank"
      rel="noreferrer"
      className="flex items-center gap-2 text-xs text-gray-500 hover:text-brand-mid transition-colors"
    
      <span>{props.icon}</span>
      <span>{props.label}</span>
    </a>
  );
}

function TeamCard({ member }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 flex flex-col items-center gap-6 hover:shadow-md transition-shadow">
      <Avatar name={member.name} />

      <div className="flex flex-col items-center gap-1 text-center">
        <h3 className="text-base font-medium text-gray-800">{member.name}</h3>
        <span className="text-xs text-brand-mid uppercase tracking-wide">EcoStress Index</span>
      </div>

      <div className="w-full flex flex-col gap-2">
        <span className="text-xs text-gray-400 uppercase tracking-wide">Contributions</span>
        <ul className="flex flex-col gap-1">
          {member.contributions.map((c) => (
            <li key={c} className="flex items-start gap-2 text-sm text-gray-600">
              <span className="text-brand-mid mt-0.5">→</span>
              <span>{c}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="w-full h-px bg-gray-100" />

      <div className="w-full flex flex-col gap-2">
        <span className="text-xs text-gray-400 uppercase tracking-wide">Contact</span>
        <ContactLink href={`mailto:${member.email}`} icon="✉️" label={member.email} />
        <ContactLink href={member.linkedin} icon="💼" label="LinkedIn" />
        <ContactLink href={member.github} icon="🐙" label="GitHub" />
      </div>
    </div>
  );
}

export default function AboutPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 font-sans">

      {/* Navbar */}
      <nav className="h-14 px-8 flex items-center justify-between border-b border-gray-100 bg-white sticky top-0 z-10">
        <span
          className="text-base font-medium text-brand-dark cursor-pointer"
          onClick={() => navigate('/')}
        >
          EcoStress Index
        </span>
        <div className="flex items-center gap-8">
          <a href="/" className="text-sm text-gray-500 hover:text-brand-dark">Home</a>
          <Button variant="primary" onClick={() => navigate('/login')}>Try the app →</Button>
        </div>
      </nav>

      {/* Header */}
      <section className="max-w-5xl mx-auto px-8 pt-20 pb-12 flex flex-col items-center text-center gap-4">
        <span className="inline-block bg-brand-light text-brand-dark text-xs font-medium px-3 py-1 rounded-full">
          The team
        </span>
        <h1 className="text-5xl font-medium text-gray-900">Built by two.</h1>
        <p className="text-base text-gray-500 max-w-lg leading-relaxed">
          EcoStress Index was built at the University of Arizona to give utility companies a smarter, data-driven tool for energy pricing and infrastructure planning.
        </p>
      </section>

      {/* Cards */}
      <section className="max-w-4xl mx-auto px-8 pb-24">
        <div className="grid grid-cols-2 gap-6">
          {team.map((member) => (
            <TeamCard key={member.name} member={member} />
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 px-8 py-8 text-center">
        <p className="text-xs text-gray-400">© 2025 EcoStress Index · University of Arizona</p>
      </footer>

    </div>
  );
}
