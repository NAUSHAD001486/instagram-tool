'use client';
import { useRouter } from 'next/navigation';
import { ArrowLeftIcon, PlayIcon } from '@heroicons/react/24/solid';

const posts = Array(15).fill({
  thumbnail: "/placeholder.jpg",
  type: 'reel'
});

export default function PostListPage({ params }) {
  const router = useRouter();
  const username = params.username;

  return (
    <div className="min-h-screen p-4 bg-black">
      <div className="w-full max-w-4xl mx-auto">
        <div className="flex items-center mb-6">
          <button onClick={() => router.back()} className="text-white hover:text-gray-300">
            <ArrowLeftIcon className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold ml-4">Post List</h1>
          <span className="ml-auto font-bold text-yellow-400">👑</span>
        </div>

        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-1">
          {posts.map((post, index) => (
            <div 
              key={index} 
              className="relative aspect-[9/16] bg-gray-800 rounded-md overflow-hidden cursor-pointer group"
              onClick={() => router.push(`/download/reel/${index + 1}`)}
            >
              <img 
                src={post.thumbnail} 
                alt={`Post ${index + 1}`} 
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" 
              />
              <div className="absolute inset-0 bg-black/30"></div>
              {post.type === 'reel' && (
                <PlayIcon className="absolute top-2 right-2 w-6 h-6 text-white drop-shadow-lg" />
              )}
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <button className="bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 px-8 rounded-full transition-colors">
            Show All Post
          </button>
        </div>
      </div>
    </div>
  );
}