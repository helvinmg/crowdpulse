import "./globals.css";
import { Providers } from "./providers";

export const metadata = {
  title: "Crowd Pulse - Hinglish Sentiment Dashboard",
  description:
    "Real-time Hinglish sentiment analysis and contrarian signals for the Indian equity market (Nifty 50)",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
