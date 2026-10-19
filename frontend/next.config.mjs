/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:5000/api/:path*',
      },
      {
        source: '/backend-health',
        destination: 'http://127.0.0.1:5000/health',
      },
    ];
  },
};

export default nextConfig;
