import './globals.css';

export const metadata = {
  title: 'Story Viewer Pro', // <--- नाम बदल दिया
  description: 'Anonymous Instagram Story Viewer and Downloader.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="relative min-h-screen main-container">
          {children}
        </div>
      </body>
    </html>
  );
}