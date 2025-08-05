// src/app/page.js
'use client';
import { AtSymbolIcon, ShieldCheckIcon } from '@heroicons/react/24/solid';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  const handleSubmit = (e) => {
    e.preventDefault();
    const username = e.target.username.value.trim();
    if(username) {
      router.push(`/confirm?username=${encodeURIComponent(username)}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-end min-h-screen p-4 text-center sm:justify-center">
      <div className="w-full max-w-md mx-auto">
        <h1 className="text-5xl font-bold tracking-wider mb-4">
          In<span className="text-purple-400">Seen</span>
        </h1>
        
        <p className="text-gray-300 mb-8 max-w-xs mx-auto">
          Just enter the username of the account whose details you want to review.
        </p>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="relative">
            <AtSymbolIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400" />
            <input
              name="username"
              type="text"
              placeholder="Instagram username"
              className="w-full bg-gray-800/50 border border-purple-500/30 rounded-full py-4 pl-12 pr-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-full py-4 text-lg hover:opacity-90 transition-opacity"
          >
            Select User
          </button>
        </form>
        
        <div className="flex items-center justify-center mt-6 text-gray-400">
          <ShieldCheckIcon className="w-5 h-5 mr-2 text-green-500" />
          <span>We do not collect any of your data.</span>
        </div>
      </div>
    </div>
  );
}