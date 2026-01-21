/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Proxy API requests to backend to avoid cross-origin cookie issues
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://abdul123233-todo-app.hf.space';
    return [
      {
        source: '/api/backend/:path*',
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
