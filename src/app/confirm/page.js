'use client';
import { Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import BackButton from '@/components/BackButton';

function LoadingSpinner() {
  return <div className="flex items-center justify-center min-h-screen text-xl font-semibold">Loading...</div>;
}

function ConfirmContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const username = searchParams.get('username') || 'error';
  const user = { name: 'Naushad alam', username: `@${username}`, avatar: '/profile-pic.jpg', stats: { posts: 166, followers: 977, following: 97 }, bio: 'azad patho Lab\nMADHEPURA' };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen p-6 pb-12 sm:pb-6">
      <BackButton />
      <main className="w-full max-w-md mx-auto text-center">
        <img src={user.avatar} alt="Profile" className="w-28 h-28 rounded-full mx-auto border-4 border-purple-500 object-cover" />
        
        <div className="flex justify-center space-x-8 my-6">
          {Object.entries(user.stats).map(([key, value]) => (
            <div key={key}>
              <p className="font-bold text-xl">{value}</p>
              <p className="text-gray-400 text-sm capitalize">{key}</p>
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold">{user.name}</h2>
        <p className="text-gray-400 text-md">{user.username}</p>
        <p className="whitespace-pre-line text-gray-300 mt-2">{user.bio}</p>

        <div className="mt-8 space-y-4">
          {/* === यहाँ बटन के स्टाइल में बदलाव किया गया है === */}
          <button 
            onClick={() => router.push(`/user/${encodeURIComponent(username)}`)} 
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-full py-3.5 text-xl 
                       transition-transform duration-200 ease-in-out 
                       hover:scale-105 active:scale-95"
          >
            Confirm User
          </button>
          <button 
            onClick={() => router.back()} 
            className="text-red-400 hover:text-red-300 font-semibold text-lg"
          >
            Change User
          </button>
        </div>
      </main>
    </div>
  );
}

export default function ConfirmPage() {
  return <Suspense fallback={<LoadingSpinner />}><ConfirmContent /></Suspense>;
}