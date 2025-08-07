'use client';
import { AtSymbolIcon, ShieldCheckIcon } from '@heroicons/react/24/solid';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  const handleSubmit = (e) => {
    e.preventDefault();
    const username = e.target.username.value.trim().replace('@', '');
    if (username) {
      router.push(`/confirm?username=${encodeURIComponent(username)}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-end min-h-screen p-6 text-center">
      <main className="w-full max-w-md mx-auto">
        {/* === यहाँ बदलाव किया गया है === */}
        <h1 className="text-5xl font-bold tracking-tight text-white">
          Story Viewer Pro
        </h1>
        <p className="text-gray-400 mt-2 mb-8 text-md">
          Anonymous Instagram Story Viewer
        </p>

        <p className="text-gray-300 mb-8 max-w-xs mx-auto">
          Just enter the username of the account whose details you want to review.
        </p>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="relative">
            <input
              name="username"
              type="text"
              placeholder="@ Instagram username"
              className="w-full bg-black/50 backdrop-blur-sm border-2 border-purple-900/50 rounded-xl py-4 px-5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 text-center text-lg"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-fuchsia-600 to-red-500 text-white font-bold rounded-xl py-4 text-xl hover:opacity-90 transition-opacity"
          >
            Select User
          </button>
        </form>
        <div className="flex items-center justify-center mt-6 text-gray-400">
          <ShieldCheckIcon className="w-5 h-5 mr-2 text-green-400" />
          <span>We do not collect any of your data.</span>
        </div>
      </main>
    </div>
  );
}