export default function Button({ variant = 'primary', onClick, children }) {
  const base = 'px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150';
  const styles = {
    primary: 'bg-brand-mid text-white hover:bg-brand-dark',
    ghost: 'border border-brand-mid text-brand-mid hover:bg-brand-light',
  };

  return (
    <button onClick={onClick} className={`${base} ${styles[variant]}`}>
      {children}
    </button>
  );
}
