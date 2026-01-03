import { useState } from 'react'
import { Layout } from './components/Layout'
import { SongList } from './pages/SongList'
import { SetlistList } from './pages/SetlistList'
import './App.css'

type Page = 'songs' | 'setlists';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('songs');

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === 'songs' && <SongList />}
      {currentPage === 'setlists' && <SetlistList />}
    </Layout>
  )
}

export default App
