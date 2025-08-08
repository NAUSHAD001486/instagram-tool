// यह फंक्शन हमारे बैकएंड API से डेटा लाने का काम करेगा
export async function fetchInstagramData(instagramUrl) {
    // .env.local से API का URL प्राप्त करें
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  
    try {
      const response = await fetch(`${apiUrl}/api/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // हम अपने बैकएंड को इंस्टाग्राम का URL भेज रहे हैं
        body: JSON.stringify({ url: instagramUrl }),
      });
  
      // अगर सर्वर से कोई एरर आता है, तो उसे यहाँ पकड़ें
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Something went wrong on the server.');
      }
  
      // अगर सब ठीक है, तो JSON डेटा वापस भेजें
      return response.json();
  
    } catch (error) {
      console.error("Failed to fetch data:", error);
      // एक कस्टम एरर मैसेज भेजें ताकि हम इसे UI में दिखा सकें
      throw new Error('Could not connect to the service. Please try again.');
    }
  }