// src/app/confirm/page.js
'use client';
import { useRouter, useSearchParams } from 'next/navigation';

export default function ConfirmPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const username = searchParams.get('username') || '@naushad__alam__12';

  const user = {
    name: 'Naushad alam',
    username: username,
    avatar: '/profile-pic.jpg',
    stats: {
      posts: 166,
      followers: 977,
      following: 97,
    },
    bio: 'azad patho Lab\nMADHEPURA',
  };

  const handleConfirm = () => {
    router.push(`/user/${encodeURIComponent(username.replace('@', ''))}`);
  };

  return (
    <div className="flex flex-col items-center justify-end min-h-screen p-4 text-center sm:justify-center">
      <div className="w-full max-w-md mx-auto">
        <img 
          src={user.avatar} 
          alt="Profile" 
          className="w-28 h-28 rounded-full mx-auto border-4 border-pink-500 object-cover"
        />
        
        <div className="flex justify-center space-x-8 my-6 text-lg">
          {Object.entries(user.stats).map(([key, value]) => (
            <div key={key}>
              <p className="font-bold text-xl">{value}</p>
              <p className="text-gray-400 text-sm capitalize">{key}</p>
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold">{user.name}</h2>
        <p className="text-gray-400 mb-4">{user.username}</p>
        <p className="whitespace-pre-line">{user.bio}</p>

        <div className="mt-8 space-y-4">
          <button 
            onClick={handleConfirm}
            className="w-full bg-gradient-to-r from-pink-600 to-red-500 text-white font-bold rounded-full py-4 text-lg hover:opacity-90 transition-opacity"
          >
            Confirm User
          </button>
          <button 
            onClick={() => router.back()}
            className="text-red-400 hover:text-red-300 font-semibold"
          >
            Change User
          </button>
        </div>
      </div>
    </div>
  );
}