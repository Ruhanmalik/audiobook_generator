import { createRoot } from 'react-dom/client';
import './index.css';
import Home from './pages/Home';
import Nav from './components/nav';

const App = () => {
  return (
    <div>
      <Nav />
      <Home />
    </div>
  );
};

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);