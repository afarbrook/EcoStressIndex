import { useState } from 'react';
import Button from '../atoms/Button';

export default function LoginCard({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit() {
    setIsLoading(true);
    setError(null);
    try {
      await onLogin(email, password);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 w-80 flex flex-col gap-4">
      <span className="text-xl font-medium text-brand-dark">EcoStress Index</span>
      <span className="text-xs text-gray-400">Sign in to continue</span>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-mid"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-mid"
      />

      {error && <p className="text-xs text-esi-red-dark">{error}</p>}

      <Button variant="primary" onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? 'Signing in...' : 'Sign in →'}
      </Button>
    </div>
  );
}
