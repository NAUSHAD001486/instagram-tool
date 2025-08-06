'use client';
import { useRouter } from 'next/navigation';
import { ArrowLeftIcon } from '@heroicons/react/24/solid';
import { SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/react/24/outline';
import { useState } from 'react';

export default function DownloadPage({ params }) {
  const router = useRouter();
  const [isMuted, setIsMuted] = useState(true);

  const reelData = {
    id: params.id,
    videoUrl: "/sample-video.mp4",
    user: {
      username: '@nausad__alam__12',
      avatar: '/profile-pic.jpg',
    },
    stats: {
      views: 52,
      likes: 4,
      comments: 2,
    }
  };

  return (
    <div className="flex flex-col h-screen bg-black">
      <div className="absolute top-0 left-0 right-0 z-10 p-4 flex items-center justify-between">
        <button onClick={() => router.back()} className="text-white bg-black/30 p-2 rounded-full">
          <ArrowLeftIcon className="w-6 h-6" />
        </button>
        <span className="text-white font-semibold text-lg drop-shadow-md">
          @{reelData.user.username} reels
        </span>
        <div></div>
      </div>
      
      <div className="relative flex-grow flex items-center justify-center">
        <video 
          src={reelData.videoUrl}
          className="w-full h-full object-contain"
          autoPlay
          loop
          muted={isMuted}
          onClick={() => setIsMuted(!isMuted)}
        />
        
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setIsMuted(!isMuted);
          }}
          className="absolute bottom-20 right-4 bg-black/40 p-3 rounded-full text-white"
        >
          {isMuted ? <SpeakerXMarkIcon className="w-6 h-6" /> : <SpeakerWaveIcon className="w-6 h-6" />}
        </button>

        <div className="absolute bottom-6 left-4 text-white drop-shadow-lg text-sm flex items-center space-x-4">
            <span>👁️ {reelData.stats.views}</span>
            <span>❤️ {reelData.stats.likes}</span>
            <span>💬 {reelData.stats.comments}</span>
        </div>
      </div>

      <div className="p-4 bg-black">
        <button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-full py-4 text-xl hover:opacity-90 transition-opacity">
          Download
        </button>
      </div>
    </div>
  );
}

// ये नया कोड नीचे जोड़ें
export async function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: '3' }
  ];
}