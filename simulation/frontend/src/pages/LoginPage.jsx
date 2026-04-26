import { useNavigate } from 'react-router-dom';
import { supabase } from '../utils/supabase';
import LoginCard from '../components/organisms/LoginCard';

export default function LoginPage() {
  const navigate = useNavigate();

  async function handleLogin(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);
    localStorage.setItem('esi_token', data.session.access_token);
    navigate('/map');
  }

  return (
    <div className="min-h-screen bg-brand-light flex items-center justify-center">
      <LoginCard onLogin={handleLogin} />
    </div>
  );
}
