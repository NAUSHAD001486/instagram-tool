// src/app/layout.js
import './globals.css';

export const metadata = {
  title: 'InSeen - Instagram Tool',
  description: 'View Instagram content anonymously',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-900 min-h-screen text-white">
        {children}
      </body>
    </html>
  );
}