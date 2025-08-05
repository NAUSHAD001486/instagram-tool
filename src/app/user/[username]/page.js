// src/app/user/[username]/page.js
'use client';
import { 
  RectangleStackIcon, 
  PlayCircleIcon,
  PlusCircleIcon,
  PhotoIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';

const ActionButton = ({ icon: Icon, text, onClick }) => (
  <div 
    className="bg-gray-800/60 rounded-xl p-4 flex flex-col items-start justify-between h-28 cursor-pointer hover:bg-gray-700/50 transition-colors"
    onClick={onClick}
  >
    <Icon className="w-8 h-8 text-gray-300" />
    <span className="font-semibold text-left">{text}</span>
  </div>
);

export default function UserDashboard({ params }) {
  const router = useRouter();
  const username = params.username;

  const user = {
    name: 'Naushad alam',
    username: `@${username}`,
    avatar: '/profile-pic.jpg',
    stats: { 
      posts: 166, 
      followers: 977, 
      following: 97 
    },
  };

  return (
    <div className="min-h-screen p-4">
      <div className="w-full max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button 
            onClick={() => router.push('/')}
            className="flex items-center text-gray-400 hover:text-white"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-1" />
            <span>Home</span>
          </button>
          
          <div className="flex items-center space-x-2 bg-yellow-400/20 text-yellow-300 px-3 py-1 rounded-full">
            <span className="font-bold text-sm">PRO</span>
            <span className="text-yellow-400">👑</span>
          </div>
        </div>

        <div className="flex items-center space-x-4 mb-4">
          <img 
            src={user.avatar} 
            alt="Profile" 
            className="w-20 h-20 rounded-full border-4 border-pink-500 object-cover"
          />
          <div className="flex justify-around flex-grow text-center">
            {Object.entries(user.stats).map(([key, value]) => (
              <div key={key}>
                <p className="font-bold text-lg">{value}</p>
                <p className="text-gray-400 text-xs capitalize">{key}</p>
              </div>
            ))}
          </div>
        </div>
        
        <h2 className="text-xl font-bold">{user.name}</h2>
        <p className="text-gray-400 text-sm">{user.username}</p>

        <div className="grid grid-cols-2 gap-4 my-8">
          <ActionButton 
            icon={PlayCircleIcon} 
            text="Show Stories" 
            onClick={() => alert('Feature coming soon!')}
          />
          <ActionButton 
            icon={RectangleStackIcon} 
            text="Show Post" 
            onClick={() => router.push(`/user/${username}/posts`)}
          />
          <ActionButton 
            icon={PlusCircleIcon} 
            text="See Highlights" 
            onClick={() => alert('Feature coming soon!')}
          />
          <ActionButton 
            icon={PhotoIcon} 
            text="Show Profile Photo" 
            onClick={() => alert('Feature coming soon!')}
          />
        </div>
        
        <button 
          onClick={() => router.push('/')}
          className="w-full bg-gray-800/60 rounded-full py-3 font-semibold hover:bg-gray-700/80 transition-colors"
        >
          Change User
        </button>
        
        <p className="text-center text-gray-500 text-xs mt-4">
          Last Update: {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  );
}