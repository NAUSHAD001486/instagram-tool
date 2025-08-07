'use client';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ConfirmPage() {
  const router = useRouter();
  const [username, setUsername] = useState('naushad__alam__12');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // URL से यूजरनेम निकालें
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const urlUsername = urlParams.get('username');
    
    if (urlUsername) {
      setUsername(urlUsername);
    }
    
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl font-semibold text-white">Loading User...</div>
      </div>
    );
  }

  const user = {
    name: 'Naushad alam',
    username: `@${username}`,
    avatar: '/profile-pic.jpg',
    stats: {
      posts: 166,
      followers: 977,
      following: 97,
    },
    bio: 'azad patho Lab\nMADHEPURA',
  };

  const handleConfirm = () => {
    router.push(`/user/${encodeURIComponent(username)}`);
  };

  return (
    <div className="flex flex-col items-center justify-end min-h-screen p-6 text-center">
      <main className="w-full max-w-md mx-auto">
        <img 
          src={user.avatar} 
          alt="Profile" 
          className="w-32 h-32 rounded-full mx-auto border-4 border-pink-500 object-cover"
        />
        
        <div className="flex justify-center space-x-10 my-6 text-lg">
          {Object.entries(user.stats).map(([key, value]) => (
            <div key={key}>
              <p className="font-bold text-2xl">{value}</p>
              <p className="text-gray-400 text-sm capitalize">{key}</p>
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold">{user.name}</h2>
        <p className="text-gray-400 mb-4 text-lg">{user.username}</p>
        <p className="whitespace-pre-line text-gray-300">{user.bio}</p>

        <div className="mt-10 space-y-4">
          <button 
            onClick={handleConfirm}
            className="w-full bg-gradient-to-r from-red-500 to-pink-500 text-white font-bold rounded-xl py-4 text-xl hover:opacity-90 transition-opacity"
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