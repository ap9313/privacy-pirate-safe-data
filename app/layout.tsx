import React from "react"
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'Safe-Data | Privacy Microservice',
  description: 'Privacy-preserving microservice for anonymizing and protecting sensitive personal information',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/large_zenitech_logo.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/large_zenitech_logo.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/large_zenitech_logo.png',
        type: 'image/svg+xml',
      },
    ],
    apple: '/large_zenitech_logo.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
