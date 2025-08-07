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
    // === यहाँ लेआउट में बदलाव किया गया है ===
    // मोबाइल पर नीचे और डेस्कटॉप पर सेंटर में
    <div className="flex flex-col items-center justify-end min-h-screen p-6 pb-16 sm:justify-center sm:pb-6">
      <main className="w-full max-w-md mx-auto text-center">
        
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-r from-fuchsia-500 to-purple-500 bg-clip-text text-transparent">
          Story Viewer Pro
        </h1>
        <p className="text-gray-300 mt-3 mb-12 text-lg tracking-wide">
          Anonymous Instagram Story Viewer
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
          
          {/* === यहाँ बटन के एनिमेशन में बदलाव किया गया है === */}
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-fuchsia-600 to-red-500 text-white font-bold rounded-xl py-4 text-xl 
                       transition-all duration-300 ease-in-out 
                       hover:scale-105 hover:shadow-lg hover:shadow-purple-500/40 
                       active:scale-95"
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