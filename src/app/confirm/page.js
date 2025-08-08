'use client';
import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import BackButton from '@/components/BackButton';
import { fetchInstagramData } from '@/services/api'; // <<< नया इम्पोर्ट

// --- यह एक लोडिंग स्क्रीन है जो डेटा आने तक दिखेगी ---
function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center">
      <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-purple-500"></div>
      <p className="mt-4 text-lg text-gray-300">Fetching profile...</p>
    </div>
  );
}

// --- यह एरर स्क्रीन है जो API फेल होने पर दिखेगी ---
function ErrorDisplay({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center p-4">
      <p className="text-xl text-red-400">Oops! Something went wrong.</p>
      <p className="text-gray-400 mt-2">{message}</p>
      <button onClick={onRetry} className="mt-6 bg-purple-600 text-white font-bold rounded-full py-2 px-6 text-lg hover:opacity-90">
        Try Again
      </button>
    </div>
  );
}


// --- यह हमारा मुख्य कंटेंट है जो अब API से डेटा लेगा ---
function ConfirmContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const username = searchParams.get('username');

  // स्टेट्स: डेटा, लोडिंग और एरर को मैनेज करने के लिए
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    const profileUrl = `https://www.instagram.com/${username}/`;
    
    try {
      const data = await fetchInstagramData(profileUrl);
      // TODO: अभी हम सिर्फ नकली डेटा को पार्स कर रहे हैं
      // बाद में हम असली 'scraped_data' को पार्स करेंगे
      const dummyData = { name: 'Naushad alam (API)', username: `@${username}`, avatar: '/profile-pic.jpg', stats: { posts: 166, followers: 977, following: 97 }, bio: 'azad patho Lab\nMADHEPURA (API)' };
      setProfileData(dummyData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (username) {
      fetchData();
    }
  }, [username]);


  // === कंडीशनल रेंडरिंग ===
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} onRetry={fetchData} />;
  if (!profileData) return null; // अगर कोई डेटा नहीं है तो कुछ न दिखाएं

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen p-6 pb-12 sm:pb-6">
      <BackButton />
      <main className="w-full max-w-md mx-auto text-center">
        {/* अब हम API से आए डेटा का उपयोग कर रहे हैं */}
        <img src={profileData.avatar} alt="Profile" className="w-28 h-28 rounded-full mx-auto border-4 border-purple-500 object-cover" />
        
        <div className="flex justify-center space-x-8 my-6">
          {Object.entries(profileData.stats).map(([key, value]) => (
            <div key={key}>
              <p className="font-bold text-xl">{value}</p>
              <p className="text-gray-400 text-sm capitalize">{key}</p>
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold">{profileData.name}</h2>
        <p className="text-gray-400 text-md">{profileData.username}</p>
        <p className="whitespace-pre-line text-gray-300 mt-2">{profileData.bio}</p>

        <div className="mt-8 space-y-4">
          <button onClick={() => router.push(`/user/${encodeURIComponent(username)}`)} className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-full py-3.5 text-xl transition-transform duration-200 ease-in-out hover:scale-105 active:scale-95">
            Confirm User
          </button>
          <button onClick={() => router.back()} className="text-red-400 hover:text-red-300 font-semibold text-lg">
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