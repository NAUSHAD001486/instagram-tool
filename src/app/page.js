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
    // === यहाँ बदलाव किया गया है ===
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <main className="w-full max-w-md mx-auto">
        
        {/* === ब्रांड का नाम अपडेट किया गया === */}
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-r from-fuchsia-500 to-purple-500 bg-clip-text text-transparent">
          Story Viewer Pro
        </h1>
        <p className="text-gray-300 mt-3 mb-12 text-lg tracking-wide">
          Anonymous Instagram Story Viewer
        </p>

        {/* अनावश्यक लाइन हटा दी गई है */}

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
            className="w-full bg-gradient-to-r from-fuchsia-600 to-red-500 text-white font-bold rounded-xl py-4 text-xl hover:opacity-90 transition-transform duration-200 ease-in-out hover:scale-105 active:scale-95"
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