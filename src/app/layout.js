import './globals.css';

export const metadata = {
  title: 'Story Viewer Pro',
  description: 'View and download Instagram content anonymously.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="main-bg">
        {children}
      </body>
    </html>
  );
}