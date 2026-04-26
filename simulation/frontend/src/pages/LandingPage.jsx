import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useInView, animate } from 'framer-motion';
import Button from '../components/atoms/Button';

const team = [
  {
    name: 'Christopher Gonzalez',
    contributions: ['Frontend architecture & design system', 'Landing page & UI animations', 'Simulation layer & map interface', 'React component library'],
    email: 'chris.gonzalez9388@gmail.com',
    linkedin: 'https://www.linkedin.com/in/christopher-gonzalez-ua/',
    github: 'https://github.com/slumppd',
  },
  {
    name: 'Alex Farbrook',
    contributions: ['Flask backend & API design', 'ESI score computation engine', 'Data source integrations', 'Repository setup & architecture'],
    email: 'afarbrook@gmail.com',
    linkedin: 'https://www.linkedin.com/in/alexfarbrook/',
    github: 'https://github.com/afarbrook',
  },
];

// --- Animated ESI counter ---
function EsiCounter({ target }) {
  const [value, setValue] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });

  useEffect(() => {
    if (!inView) return;
    const controls = animate(0, target, {
      duration: 2,
      ease: 'easeOut',
      onUpdate: (v) => setValue(v),
    });
    return () => controls.stop();
  }, [inView, target]);

  const color = value < 0.4 ? '#3b6d11' : value < 0.7 ? '#854f0b' : '#a32d2d';
  return (
    <span ref={ref} style={{ color }} className="text-8xl font-medium tabular-nums">
      {value.toFixed(2)}
    </span>
  );
}

// --- Gradient mesh background ---
function MeshBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden -z-10">
      <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-20 blur-3xl animate-pulse"
        style={{ background: '#97c459' }} />
      <div className="absolute top-20 right-0 w-80 h-80 rounded-full opacity-20 blur-3xl animate-pulse"
        style={{ background: '#ef9f27', animationDelay: '1s' }} />
      <div className="absolute bottom-0 left-1/2 w-72 h-72 rounded-full opacity-20 blur-3xl animate-pulse"
        style={{ background: '#e24b4a', animationDelay: '2s' }} />
    </div>
  );
}

// --- Live mini-map preview ---
function MiniMapPreview() {
  const tracts = [
    { x: 60, y: 80, w: 80, h: 60, score: 0.2 },
    { x: 140, y: 80, w: 70, h: 60, score: 0.45 },
    { x: 210, y: 80, w: 90, h: 60, score: 0.71 },
    { x: 60, y: 140, w: 90, h: 70, score: 0.55 },
    { x: 150, y: 140, w: 80, h: 70, score: 0.83 },
    { x: 230, y: 140, w: 70, h: 70, score: 0.38 },
    { x: 60, y: 210, w: 70, h: 60, score: 0.67 },
    { x: 130, y: 210, w: 100, h: 60, score: 0.91 },
    { x: 230, y: 210, w: 70, h: 60, score: 0.29 },
  ];

  function scoreToColor(score) {
    if (score < 0.5) {
      const t = score / 0.5;
      const r = Math.round(59 + t * (239 - 59));
      const g = Math.round(109 + t * (159 - 109));
      const b = Math.round(17 + t * (39 - 17));
      return `rgb(${r},${g},${b})`;
    } else {
      const t = (score - 0.5) / 0.5;
      const r = Math.round(239 + t * (226 - 239));
      const g = Math.round(159 + t * (75 - 159));
      const b = Math.round(39 + t * (74 - 39));
      return `rgb(${r},${g},${b})`;
    }
  }

  return (
    <div className="relative w-80 h-80 rounded-xl overflow-hidden border border-white/20 shadow-2xl">
      <div className="absolute inset-0 bg-gray-900" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 360 300">
        {tracts.map((t, i) => (
          <motion.rect
            key={i}
            x={t.x} y={t.y} width={t.w} height={t.h}
            fill={scoreToColor(t.score)}
            fillOpacity={0.75}
            stroke="white"
            strokeWidth={1}
            initial={{ fillOpacity: 0 }}
            animate={{ fillOpacity: 0.75 }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
          />
        ))}
      </svg>
      <div className="absolute bottom-3 left-3 bg-black/60 rounded-lg px-3 py-1">
        <span className="text-xs text-white">Tucson, AZ — live preview</span>
      </div>
      <div className="absolute inset-0 backdrop-blur-[1px]" />
    </div>
  );
}

// --- Pulsing heatmap blob ---
function HeatmapBlob() {
  return (
    <div className="absolute inset-0 overflow-hidden -z-10">
      {[
        { color: '#e24b4a', top: '10%', left: '10%', delay: '0s' },
        { color: '#ef9f27', top: '40%', left: '60%', delay: '0.8s' },
        { color: '#e24b4a', top: '70%', left: '30%', delay: '1.6s' },
      ].map((blob, i) => (
        <div
          key={i}
          className="absolute w-64 h-64 rounded-full blur-3xl opacity-30 animate-pulse"
          style={{
            background: blob.color,
            top: blob.top,
            left: blob.left,
            animationDelay: blob.delay,
          }}
        />
      ))}
    </div>
  );
}

// --- Feature card with scroll animation ---
function FeatureCard({ f, index }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -40 }}
      animate={inView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="rounded-xl border border-gray-100 p-6 flex flex-col gap-3 hover:shadow-md transition-shadow bg-white"
    >
      <span className={`w-9 h-9 flex items-center justify-center rounded-lg text-lg ${f.color}`}>
        {f.icon}
      </span>
      <h3 className="text-base font-medium text-gray-800">{f.title}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{f.body}</p>
    </motion.div>
  );
}

// --- How it works step with connecting line ---
function HowStep({ step, index, total }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });

  return (
    <div ref={ref} className="flex flex-col items-center gap-3 relative">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: index * 0.2 }}
        className="flex flex-col items-center gap-3 text-center"
      >
        <span className="text-3xl font-medium text-brand-mid">{step.number}</span>
        <h3 className="text-base font-medium text-gray-800">{step.title}</h3>
        <p className="text-sm text-gray-500 leading-relaxed">{step.body}</p>
      </motion.div>

      {index < total - 1 && (
        <motion.div
          initial={{ scaleX: 0 }}
          animate={inView ? { scaleX: 1 } : {}}
          transition={{ duration: 0.6, delay: index * 0.2 + 0.3 }}
          className="hidden md:block absolute top-4 left-full w-full h-px bg-brand-mid origin-left"
          style={{ width: 'calc(100% - 2rem)', left: 'calc(50% + 1rem)' }}
        />
      )}
    </div>
  );
}

// --- Data ---
const features = [
  { color: 'bg-brand-light text-brand-dark', icon: '🤖', title: 'AI-adaptive weights', body: 'Google Gemini calibrates ESI component weights per city — Tucson gets a high heat island weight, Seattle gets air quality.' },
  { color: 'bg-esi-amber-light text-esi-amber-dark', icon: '📡', title: 'Real sensor data', body: 'Pulls live readings from AirNow, PurpleAir, U.S. EIA, and NASA VIIRS. No synthetic data.' },
  { color: 'bg-esi-red-light text-esi-red-dark', icon: '⚡', title: 'Dynamic pricing', body: 'ESI score converts directly to a $/kWh recommendation, with a tunable alpha coefficient per utility.' },
  { color: 'bg-esi-green-light text-esi-green-dark', icon: '🌍', title: 'Any city, worldwide', body: 'Census TIGER boundaries + Nominatim geocoding means global coverage out of the box.' },
];

const steps = [
  { number: '01', title: 'Search a city', body: 'Type any city name. Boundaries are fetched from the U.S. Census TIGER API in seconds.' },
  { number: '02', title: 'Score neighborhoods', body: 'Gemini assigns city-specific weights. Four data sources score each census tract automatically.' },
  { number: '03', title: 'See the price', body: 'Every neighborhood gets a dynamic $/kWh recommendation based on its ESI score.' },
];

const sources = [
  { label: 'Air quality', value: 'EPA AirNow + PurpleAir' },
  { label: 'Energy use', value: 'U.S. EIA Open Data API' },
  { label: 'Light pollution', value: 'NASA VIIRS Day/Night Band' },
  { label: 'Heat island', value: 'NASA Landsat thermal imagery' },
  { label: 'City boundaries', value: 'U.S. Census TIGER/Line API' },
  { label: 'Geocoding', value: 'OpenStreetMap Nominatim' },
];

// --- Page ---
export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white font-sans">

      {/* Navbar */}
      <nav className="h-14 px-8 flex items-center justify-between border-b border-gray-100 sticky top-0 bg-white/90 backdrop-blur z-10 scroll-snap-align-none">
        <span className="text-base font-medium text-brand-dark">EcoStress Index</span>
          <div className="flex items-center gap-8">
            <a href="#about" className="text-sm text-gray-500 hover:text-brand-dark">About</a>
            <a href="#features" className="text-sm text-gray-500 hover:text-brand-dark">Features</a>
            <a href="#how" className="text-sm text-gray-500 hover:text-brand-dark">How it works</a>
            <Button variant="primary" onClick={() => navigate('/login')}>Try the app →</Button>
          </div>
      </nav>

      {/* Hero */}
      <section className="relative min-h-screen max-w-6xl mx-auto px-8 flex flex-col md:flex-row items-center justify-center gap-16">
        <MeshBackground />
        <div className="flex flex-col items-start gap-6 flex-1">
          <span className="inline-block bg-brand-light text-brand-dark text-xs font-medium px-3 py-1 rounded-full">
            Built for APS · SRP · utility companies
          </span>
          <h1 className="text-5xl font-medium text-gray-900 leading-tight">
            Environmental stress scores.<br />Smarter energy pricing.
          </h1>
          <p className="text-base text-gray-500 max-w-xl leading-relaxed">
            Score any neighborhood's environmental burden using AI-weighted sensor data from AirNow, NASA, and the EIA. Price electricity dynamically based on real impact — greener neighborhoods pay less.
          </p>
          <div className="flex gap-3 mt-2">
            <Button variant="primary" onClick={() => navigate('/login')}>Try the app →</Button>
            <Button variant="ghost" onClick={() => document.getElementById('how').scrollIntoView({ behavior: 'smooth' })}>
              See how it works
            </Button>
          </div>
        </div>
        <div className="flex-1 flex justify-center">
          <div className="flex flex-col items-center">
            <div className="flex flex-col items-center gap-1 mb-4">
              <span className="text-xs text-gray-400 uppercase tracking-wide">Tucson avg ESI</span>
              <EsiCounter target={0.74} />
            </div>
            <MiniMapPreview />
          </div>
        </div>
      </section>

    {/* About */}
    <section id="about" className="min-h-screen max-w-4xl mx-auto px-8 flex flex-col justify-center gap-12">
      <div className="flex flex-col items-center text-center gap-4">
        <span className="inline-block bg-brand-light text-brand-dark text-xs font-medium px-3 py-1 rounded-full">
          The team
        </span>
        <h2 className="text-4xl font-medium text-gray-900">Built by two.</h2>
        <p className="text-base text-gray-500 max-w-lg leading-relaxed">
          EcoStress Index was built at the University of Arizona to give utility companies a smarter, data-driven tool for energy pricing and infrastructure planning.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {team.map((member) => (
          <div key={member.name} className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 flex flex-col items-center gap-6 hover:shadow-md transition-shadow">
            <div className="w-24 h-24 rounded-full bg-brand-light flex items-center justify-center shrink-0">
              <span className="text-2xl font-medium text-brand-dark">
                {member.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>

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
              <a href={`mailto:${member.email}`} className="flex items-center gap-2 text-xs text-gray-500 hover:text-brand-mid transition-colors">
                <span>✉️</span><span>{member.email}</span>
              </a>
              <a href={member.linkedin} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-xs text-gray-500 hover:text-brand-mid transition-colors">
                <span>💼</span><span>LinkedIn</span>
              </a>
              <a href={member.github} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-xs text-gray-500 hover:text-brand-mid transition-colors">
                <span>🐙</span><span>GitHub</span>
              </a>
            </div>
          </div>
        ))}
      </div>
    </section>

      {/* Feature Cards */}
      <section id="features" className="min-h-screen max-w-5xl mx-auto px-8 flex flex-col justify-center gap-8">
        <h2 className="text-xl font-medium text-gray-800 text-center">Why EcoStress</h2>
        <div className="grid grid-cols-2 gap-4">
          {features.map((f, i) => <FeatureCard key={f.title} f={f} index={i} />)}
        </div>
      </section>

      {/* Problem Statement */}
      <section className="relative min-h-screen bg-esi-red-light px-8 flex flex-col justify-center overflow-hidden">
        <HeatmapBlob />
        <div className="max-w-3xl mx-auto flex flex-col gap-4 relative z-10">
          <span className="text-xs text-esi-red-dark uppercase tracking-wide font-medium">The problem</span>
          <p className="text-4xl font-medium text-gray-800 leading-snug">
            APS cannot support current demand — electricity use in Arizona grew 8% in 2025, four times the national average.
          </p>
          <p className="text-base text-gray-600 leading-relaxed mt-4">
            EcoStress gives utility companies a data-driven siting and pricing tool before the grid breaks.
          </p>
        </div>
      </section>

      {/* How it Works */}
      <section id="how" className="min-h-screen max-w-5xl mx-auto px-8 flex flex-col justify-center gap-12">
        <h2 className="text-xl font-medium text-gray-800 text-center">How it works</h2>
        <div className="grid grid-cols-3 gap-8 relative">
          {steps.map((s, i) => <HowStep key={s.number} step={s} index={i} total={steps.length} />)}
        </div>
      </section>

      {/* CTA Banner */}
      <section className="min-h-screen bg-brand-dark px-8 flex flex-col items-center justify-center gap-6 text-center">
        <h2 className="text-4xl font-medium text-white">Ready to score your city?</h2>
        <p className="text-base text-brand-light max-w-md leading-relaxed">
          Join utility companies using real environmental data to make smarter infrastructure decisions.
        </p>
        <Button variant="ghost" onClick={() => navigate('/login')}>
          Get started →
        </Button>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 px-8 py-12">
        <div className="max-w-5xl mx-auto flex flex-col gap-6">
          <span className="text-sm font-medium text-brand-dark">EcoStress Index</span>
          <div className="grid grid-cols-3 gap-4">
            {sources.map((s) => (
              <div key={s.label} className="flex flex-col gap-1">
                <span className="text-xs text-gray-400">{s.label}</span>
                <span className="text-xs text-gray-600">{s.value}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400">© 2025 EcoStress Index. Built for APS · SRP · utility companies.</p>
        </div>
      </footer>

    </div>
  );
}
