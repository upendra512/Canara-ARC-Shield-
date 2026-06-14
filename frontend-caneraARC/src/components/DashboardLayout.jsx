import Navbar from './Navbar'
import Footer from './Footer'

export default function DashboardLayout({ children }) {
  return (
    <div className="flex min-h-full bg-surface">
      <Navbar />
      <div className="flex min-h-screen flex-1 flex-col pt-14 lg:pt-0">
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
        <Footer />
      </div>
    </div>
  )
}
